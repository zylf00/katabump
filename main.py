#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动续期脚本 - GitHub Actions版本
支持多种浏览器方案和智能Turnstile处理
"""

import os
import time
import asyncio
import random
import sys
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('renew.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class ServerRenewBot:
    def __init__(self):
        # 从环境变量获取配置
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.login_url = os.getenv('LOGIN_URL') or 'https://dashboard.katabump.com/auth/login'
        self.renew_url = os.getenv('RENEW_URL') or 'https://dashboard.katabump.com/servers/edit?id=124653'
        
        # 验证配置
        if not self.email or not self.password:
            logger.error('❌ 请设置 EMAIL 和 PASSWORD 环境变量')
            sys.exit(1)
        
        # 验证URL格式
        if not self.login_url.startswith('http'):
            logger.error(f'❌ 无效的登录URL: {self.login_url}')
            sys.exit(1)
            
        if not self.renew_url.startswith('http'):
            logger.error(f'❌ 无效的续期URL: {self.renew_url}')
            sys.exit(1)
        
        logger.info(f'🚀 开始执行续期任务 - {datetime.now()}')
        logger.info(f'📧 邮箱: {self.email[:3]}***{self.email.split("@")[1]}')
        logger.info(f'🔗 登录URL: {self.login_url}')
        logger.info(f'🔗 续期URL: {self.renew_url}')
    
    def random_delay(self, min_sec=1, max_sec=3):
        """随机延迟，模拟人类行为"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def human_type(self, element, text):
        """模拟人类输入"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    async def run_with_selenium(self):
        """使用 undetected-chromedriver 方案"""
        try:
            import undetected_chromedriver as uc
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, NoSuchElementException
            
            logger.info('🔧 初始化 undetected-chromedriver...')
            
            options = uc.ChromeOptions()
            options.add_argument('--headless=new')  # 新版headless模式
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--no-first-run')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-ipc-flooding-protection')
            
            # 随机User-Agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # 使用兼容的实验选项设置方式
            try:
                # 尝试新的设置方式
                prefs = {
                    "profile.default_content_setting_values.notifications": 2,
                    "profile.managed_default_content_settings.images": 2
                }
                options.add_experimental_option("prefs", prefs)
            except Exception as e:
                logger.warning(f'实验选项设置失败: {e}')
            
            # 创建驱动实例，使用更兼容的参数
            driver = uc.Chrome(
                options=options, 
                version_main=None,
                driver_executable_path=None,
                browser_executable_path=None,
                use_subprocess=True
            )
            
            # 反检测脚本
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                window.chrome = {runtime: {}, loadTimes: function() {}, csi: function() {}, app: {}};
            """)
            
            wait = WebDriverWait(driver, 30)
            
            try:
                # === 登录流程 ===
                logger.info('🌐 访问登录页面...')
                driver.get(self.login_url)
                self.random_delay(2, 4)
                
                # 等待登录表单加载
                try:
                    login_form = wait.until(
                        EC.any_of(
                            EC.presence_of_element_located((By.ID, 'login-form')),
                            EC.presence_of_element_located((By.ID, 'email'))
                        )
                    )
                    logger.info('✅ 登录表单已加载')
                except TimeoutException:
                    logger.error('❌ 登录表单加载超时')
                    driver.save_screenshot('/tmp/login_form_timeout.png')
                    return False
                
                # 输入登录信息
                try:
                    email_field = wait.until(EC.element_to_be_clickable((By.ID, 'email')))
                    password_field = driver.find_element(By.ID, 'password')
                    login_btn = driver.find_element(By.ID, 'submit')
                    
                    logger.info('⌨️ 输入登录信息...')
                    self.human_type(email_field, self.email)
                    self.random_delay(0.5, 1.5)
                    self.human_type(password_field, self.password)
                    self.random_delay(1, 2)
                    
                    logger.info('🖱️ 点击登录按钮...')
                    login_btn.click()
                    
                except (TimeoutException, NoSuchElementException) as e:
                    logger.error(f'❌ 登录元素未找到: {e}')
                    driver.save_screenshot('/tmp/login_elements_not_found.png')
                    return False
                
                # 等待登录完成
                logger.info('⏳ 等待登录完成...')
                time.sleep(5)
                
                # 检查登录结果
                current_url = driver.current_url
                if 'dashboard' not in current_url and 'admin' not in current_url:
                    logger.error(f'❌ 登录失败，当前URL: {current_url}')
                    
                    # 检查是否有错误信息
                    try:
                        error_elements = driver.find_elements(By.CSS_SELECTOR, '.alert-danger, .error, .invalid-feedback')
                        for elem in error_elements:
                            if elem.is_displayed():
                                logger.error(f'登录错误信息: {elem.text}')
                    except:
                        pass
                    
                    driver.save_screenshot('/tmp/login_failed.png')
                    return False
                
                logger.info('✅ 登录成功！')
                
                # === 续期流程 ===
                logger.info('🌐 访问续期页面...')
                driver.get(self.renew_url)
                self.random_delay(3, 5)
                
                # 查找续期按钮
                renew_button_selectors = [
                    'button.btn.btn-outline-primary',
                    'button[type="submit"]',
                    '.btn-primary',
                    '//button[contains(text(), "续期")]',
                    '//button[contains(text(), "Renew")]',
                    '//button[contains(text(), "延期")]'
                ]
                
                renew_btn = None
                for selector in renew_button_selectors:
                    try:
                        if selector.startswith('//'):
                            # 这是XPath选择器
                            renew_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        else:
                            # 这是CSS选择器
                            renew_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        
                        logger.info(f'✅ 找到续期按钮: {selector}')
                        break
                    except TimeoutException:
                        continue
                
                if not renew_btn:
                    logger.error('❌ 未找到续期按钮')
                    driver.save_screenshot('/tmp/renew_button_not_found.png')
                    return False
                
                logger.info('🖱️ 点击续期按钮...')
                driver.execute_script("arguments[0].scrollIntoView(true);", renew_btn)
                time.sleep(1)
                renew_btn.click()
                
                # === Turnstile验证处理 ===
                logger.info('🔐 开始处理Turnstile验证...')
                await self.handle_turnstile_selenium(driver, wait)
                
                # 最终确认
                time.sleep(3)
                try:
                    # 查找可能的确认按钮
                    confirm_selectors = [
                        'button[type="submit"]',
                        '.btn-success',
                        '.btn-primary:not(.btn-outline-primary)',
                        '//button[contains(text(), "确认")]',
                        '//button[contains(text(), "Confirm")]',
                        '//button[contains(text(), "完成")]'
                    ]
                    
                    for selector in confirm_selectors:
                        try:
                            if selector.startswith('//'):
                                # XPath选择器
                                confirm_btn = driver.find_element(By.XPATH, selector)
                            else:
                                # CSS选择器
                                confirm_btn = driver.find_element(By.CSS_SELECTOR, selector)
                            
                            if confirm_btn.is_displayed() and confirm_btn.is_enabled():
                                logger.info(f'🖱️ 点击确认按钮: {selector}')
                                confirm_btn.click()
                                time.sleep(3)
                                break
                        except (NoSuchElementException, TimeoutException):
                            continue
                            
                except Exception as e:
                    logger.info(f'ℹ️ 没有额外的确认步骤: {e}')
                
                # 保存成功截图
                driver.save_screenshot('/tmp/selenium_success.png')
                logger.info('✅ Selenium方案执行完成！')
                return True
                
            except Exception as e:
                logger.error(f'❌ Selenium方案执行出错: {e}')
                driver.save_screenshot('/tmp/selenium_error.png')
                return False
                
        except ImportError:
            logger.error('❌ undetected-chromedriver 未安装')
            return False
        except Exception as e:
            logger.error(f'❌ Selenium初始化失败: {e}')
            return False
        finally:
            try:
                if 'driver' in locals():
                    driver.quit()
            except:
                pass
    
    async def handle_turnstile_selenium(self, driver, wait):
        """处理Turnstile验证 - Selenium版本"""
        max_wait_time = 90  # 最大等待90秒
        start_time = time.time()
        
        logger.info('🔍 寻找Turnstile验证框...')
        
        while time.time() - start_time < max_wait_time:
            try:
                # 方法1: 检查cf-turnstile-response是否有值
                try:
                    token_element = driver.find_element(By.NAME, 'cf-turnstile-response')
                    token_value = token_element.get_attribute('value')
                    
                    if token_value and len(token_value) > 10:
                        logger.info('✅ 检测到Turnstile验证已完成！')
                        return True
                except (NoSuchElementException, TimeoutException):
                    pass
                
                # 方法2: 尝试找到并点击Turnstile元素
                turnstile_selectors = [
                    '[data-sitekey]',
                    '.cf-turnstile',
                    'iframe[src*="turnstile"]',
                    '[id*="turnstile"]',
                    '[class*="turnstile"]'
                ]
                
                for selector in turnstile_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed():
                                logger.info(f'🎯 找到Turnstile元素: {selector}')
                                
                                # 滚动到元素位置
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                time.sleep(1)
                                
                                # 模拟鼠标悬停和点击
                                from selenium.webdriver.common.action_chains import ActionChains
                                actions = ActionChains(driver)
                                actions.move_to_element(element).pause(1).click().perform()
                                
                                logger.info('🖱️ 已点击Turnstile元素')
                                time.sleep(3)
                                break
                    except Exception as e:
                        continue
                
                # 方法3: 尝试处理iframe中的Turnstile
                try:
                    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                    for iframe in iframes:
                        src = iframe.get_attribute('src') or ''
                        if 'turnstile' in src or 'cloudflare' in src:
                            logger.info('🔍 找到Turnstile iframe，尝试切换...')
                            driver.switch_to.frame(iframe)
                            
                            # 在iframe中查找checkbox
                            try:
                                checkbox = driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"], .checkbox, [role="checkbox"]')
                                if checkbox.is_displayed():
                                    checkbox.click()
                                    logger.info('✅ 点击了Turnstile复选框')
                                    time.sleep(2)
                            except:
                                pass
                            
                            driver.switch_to.default_content()
                            time.sleep(2)
                            break
                except Exception as e:
                    driver.switch_to.default_content()
                
                # 方法4: 检查页面是否有成功指示
                success_indicators = [
                    '//*[contains(@class, "success")]',
                    '//*[contains(@class, "verified")]',
                    '//*[contains(text(), "验证成功")]',
                    '//*[contains(text(), "Success")]',
                    '//*[contains(text(), "Verified")]'
                ]
                
                for indicator in success_indicators:
                    try:
                        element = driver.find_element(By.XPATH, indicator)
                        if element.is_displayed():
                            logger.info('✅ 检测到验证成功指示！')
                            return True
                    except:
                        continue
                
                # 每5秒输出一次等待信息
                elapsed = int(time.time() - start_time)
                if elapsed % 5 == 0 and elapsed > 0:
                    logger.info(f'⏳ Turnstile验证等待中... ({elapsed}/{max_wait_time}秒)')
                
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f'⚠️ Turnstile处理中的异常: {e}')
                time.sleep(2)
        
        logger.warning('⚠️ Turnstile验证等待超时，但继续执行...')
        return False
    
    async def run_with_playwright(self):
        """使用 Playwright 方案"""
        try:
            from playwright.async_api import async_playwright
            
            logger.info('🔧 初始化 Playwright...')
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=random.choice([
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    ])
                )
                
                page = await context.new_page()
                
                # 注入反检测脚本
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    window.chrome = {runtime: {}, loadTimes: function() {}, csi: function() {}, app: {}};
                """)
                
                try:
                    # 登录流程
                    logger.info('🌐 Playwright: 访问登录页面...')
                    await page.goto(self.login_url, wait_until='networkidle')
                    
                    await page.wait_for_selector('#email', timeout=30000)
                    
                    # 模拟人类输入
                    await page.fill('#email', '')  # 先清空
                    await page.type('#email', self.email, delay=random.randint(50, 150))
                    await page.wait_for_timeout(random.randint(500, 1500))
                    
                    await page.fill('#password', '')
                    await page.type('#password', self.password, delay=random.randint(50, 150))
                    await page.wait_for_timeout(random.randint(1000, 2000))
                    
                    logger.info('🖱️ Playwright: 点击登录...')
                    await page.click('#submit')
                    await page.wait_for_load_state('networkidle')
                    
                    # 检查登录结果
                    current_url = page.url
                    if 'dashboard' not in current_url and 'admin' not in current_url:
                        logger.error(f'❌ Playwright: 登录失败，当前URL: {current_url}')
                        await page.screenshot(path='/tmp/playwright_login_failed.png')
                        return False
                    
                    logger.info('✅ Playwright: 登录成功！')
                    
                    # 续期流程
                    logger.info('🌐 Playwright: 访问续期页面...')
                    await page.goto(self.renew_url, wait_until='networkidle')
                    
                    # 查找并点击续期按钮
                    renew_selectors = [
                        'button.btn.btn-outline-primary',
                        'button[type="submit"]',
                        '.btn-primary'
                    ]
                    
                    renew_clicked = False
                    for selector in renew_selectors:
                        try:
                            await page.wait_for_selector(selector, timeout=10000)
                            await page.click(selector)
                            logger.info(f'✅ Playwright: 点击续期按钮: {selector}')
                            renew_clicked = True
                            break
                        except:
                            continue
                    
                    if not renew_clicked:
                        logger.error('❌ Playwright: 未找到续期按钮')
                        await page.screenshot(path='/tmp/playwright_no_renew_button.png')
                        return False
                    
                    # 处理Turnstile
                    logger.info('🔐 Playwright: 处理Turnstile验证...')
                    await self.handle_turnstile_playwright(page)
                    
                    # 等待完成
                    await page.wait_for_timeout(5000)
                    await page.screenshot(path='/tmp/playwright_final.png')
                    
                    logger.info('✅ Playwright方案执行完成！')
                    return True
                    
                except Exception as e:
                    logger.error(f'❌ Playwright执行出错: {e}')
                    await page.screenshot(path='/tmp/playwright_error.png')
                    return False
                finally:
                    await browser.close()
                    
        except ImportError:
            logger.error('❌ Playwright 未安装')
            return False
        except Exception as e:
            logger.error(f'❌ Playwright初始化失败: {e}')
            return False
    
    async def run_with_basic_selenium(self):
        """使用基础 Selenium 作为备用方案"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, NoSuchElementException
            
            logger.info('🔧 初始化基础 Selenium（备用方案）...')
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver, 30)
            
            try:
                # 登录流程
                logger.info('🌐 基础Selenium: 访问登录页面...')
                driver.get(self.login_url)
                time.sleep(3)
                
                # 输入登录信息
                email_field = wait.until(EC.element_to_be_clickable((By.ID, 'email')))
                password_field = driver.find_element(By.ID, 'password')
                login_btn = driver.find_element(By.ID, 'submit')
                
                email_field.clear()
                email_field.send_keys(self.email)
                time.sleep(1)
                
                password_field.clear()
                password_field.send_keys(self.password)
                time.sleep(1)
                
                logger.info('🖱️ 基础Selenium: 点击登录...')
                login_btn.click()
                time.sleep(5)
                
                # 检查登录结果
                if 'dashboard' not in driver.current_url:
                    logger.error(f'❌ 基础Selenium: 登录失败，当前URL: {driver.current_url}')
                    driver.save_screenshot('/tmp/basic_selenium_login_failed.png')
                    return False
                
                logger.info('✅ 基础Selenium: 登录成功！')
                
                # 续期流程
                logger.info('🌐 基础Selenium: 访问续期页面...')
                driver.get(self.renew_url)
                time.sleep(3)
                
                # 查找续期按钮
                renew_btn = None
                selectors = [
                    'button.btn.btn-outline-primary',
                    'button[type="submit"]',
                    '.btn-primary'
                ]
                
                for selector in selectors:
                    try:
                        renew_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        logger.info(f'✅ 基础Selenium: 找到续期按钮: {selector}')
                        break
                    except TimeoutException:
                        continue
                
                if not renew_btn:
                    logger.error('❌ 基础Selenium: 未找到续期按钮')
                    driver.save_screenshot('/tmp/basic_selenium_no_button.png')
                    return False
                
                logger.info('🖱️ 基础Selenium: 点击续期按钮...')
                renew_btn.click()
                time.sleep(5)
                
                # 简单等待（不处理复杂的Turnstile）
                logger.info('⏳ 基础Selenium: 等待页面响应...')
                time.sleep(10)
                
                driver.save_screenshot('/tmp/basic_selenium_final.png')
                logger.info('✅ 基础Selenium: 执行完成')
                return True
                
            except Exception as e:
                logger.error(f'❌ 基础Selenium执行错误: {e}')
                driver.save_screenshot('/tmp/basic_selenium_error.png')
                return False
            finally:
                driver.quit()
                
        except ImportError:
            logger.error('❌ 基础Selenium不可用')
            return False
        except Exception as e:
            logger.error(f'❌ 基础Selenium初始化失败: {e}')
            return False
    
    async def handle_turnstile_playwright(self, page):
        """处理Turnstile验证 - Playwright版本"""
        max_wait_time = 90
        
        try:
            # 等待Turnstile加载
            await page.wait_for_timeout(5000)
            
            # 尝试多种方法处理Turnstile
            turnstile_selectors = [
                '[data-sitekey]',
                '.cf-turnstile',
                'iframe[src*="turnstile"]'
            ]
            
            for selector in turnstile_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=10000)
                    if element:
                        logger.info(f'🎯 Playwright: 找到Turnstile: {selector}')
                        await element.hover()
                        await page.wait_for_timeout(1000)
                        await element.click()
                        await page.wait_for_timeout(3000)
                        break
                except:
                    continue
            
            # 等待验证完成
            try:
                await page.wait_for_function(
                    '''() => {
                        const token = document.querySelector('[name="cf-turnstile-response"]');
                        return token && token.value && token.value.length > 10;
                    }''',
                    timeout=max_wait_time * 1000
                )
                logger.info('✅ Playwright: Turnstile验证完成！')
                return True
            except:
                logger.warning('⚠️ Playwright: Turnstile验证可能未完成')
                return False
                
        except Exception as e:
            logger.warning(f'⚠️ Playwright: Turnstile处理异常: {e}')
            return False
        """处理Turnstile验证 - Playwright版本"""
        max_wait_time = 90
        
        try:
            # 等待Turnstile加载
            await page.wait_for_timeout(5000)
            
            # 尝试多种方法处理Turnstile
            turnstile_selectors = [
                '[data-sitekey]',
                '.cf-turnstile',
                'iframe[src*="turnstile"]'
            ]
            
            for selector in turnstile_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=10000)
                    if element:
                        logger.info(f'🎯 Playwright: 找到Turnstile: {selector}')
                        await element.hover()
                        await page.wait_for_timeout(1000)
                        await element.click()
                        await page.wait_for_timeout(3000)
                        break
                except:
                    continue
            
            # 等待验证完成
            try:
                await page.wait_for_function(
                    '''() => {
                        const token = document.querySelector('[name="cf-turnstile-response"]');
                        return token && token.value && token.value.length > 10;
                    }''',
                    timeout=max_wait_time * 1000
                )
                logger.info('✅ Playwright: Turnstile验证完成！')
                return True
            except:
                logger.warning('⚠️ Playwright: Turnstile验证可能未完成')
                return False
                
        except Exception as e:
            logger.warning(f'⚠️ Playwright: Turnstile处理异常: {e}')
            return False
    
    async def run(self):
        """主执行函数"""
        success = False
        
        # 尝试方案1: undetected-chromedriver
        logger.info('📋 === 尝试方案1: undetected-chromedriver ===')
        try:
            success = await self.run_with_selenium()
            if success:
                logger.info('🎉 方案1执行成功！')
                return True
        except Exception as e:
            logger.error(f'❌ 方案1执行异常: {e}')
        
        # 如果方案1失败，尝试方案2: Playwright
        if not success:
            logger.info('📋 === 尝试方案2: Playwright ===')
            try:
                success = await self.run_with_playwright()
                if success:
                    logger.info('🎉 方案2执行成功！')
                    return True
            except Exception as e:
                logger.error(f'❌ 方案2执行异常: {e}')
        
        # 如果前两个方案都失败，尝试方案3: 基础Selenium
        if not success:
            logger.info('📋 === 尝试方案3: 基础Selenium ===')
            try:
                success = await self.run_with_basic_selenium()
                if success:
                    logger.info('🎉 方案3执行成功！')
                    return True
            except Exception as e:
                logger.error(f'❌ 方案3执行异常: {e}')
        
        # 所有方案都失败
        if not success:
            logger.error('💥 所有方案都失败了！')
            return False
        
        return success

async def main():
    """程序入口"""
    try:
        bot = ServerRenewBot()
        success = await bot.run()
        
        if success:
            logger.info('🎉 ===== 续期任务执行成功！=====')
            sys.exit(0)
        else:
            logger.error('💥 ===== 续期任务执行失败！=====')
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info('⚠️ 用户中断执行')
        sys.exit(1)
    except Exception as e:
        logger.error(f'💥 程序执行异常: {e}')
        sys.exit(1)

if __name__ == '__main__':
    # 设置事件循环策略（Windows兼容）
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 运行主程序
    asyncio.run(main())
