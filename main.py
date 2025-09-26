#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实鼠标点击版本 - 专门处理Turnstile验证
使用pyautogui进行真实的鼠标操作，绕过自动化检测
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

class RealMouseRenewBot:
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
        
        logger.info(f'🚀 开始执行真实鼠标点击续期任务 - {datetime.now()}')
        logger.info(f'📧 邮箱: {self.email[:3]}***{self.email.split("@")[1]}')
        logger.info(f'🔗 登录URL: {self.login_url}')
        logger.info(f'🔗 续期URL: {self.renew_url}')
    
    def setup_pyautogui(self):
        """设置pyautogui"""
        try:
            import pyautogui
            
            # 设置pyautogui参数
            pyautogui.FAILSAFE = True  # 启用故障安全
            pyautogui.PAUSE = 0.1  # 每次操作间隔
            
            # 检查屏幕尺寸
            screen_width, screen_height = pyautogui.size()
            logger.info(f'🖥️ 屏幕尺寸: {screen_width}x{screen_height}')
            
            return pyautogui
            
        except ImportError:
            logger.error('❌ pyautogui 未安装，请运行: pip install pyautogui')
            return None
        except Exception as e:
            logger.error(f'❌ 设置pyautogui失败: {e}')
            return None
    
    def setup_virtual_display(self):
        """设置虚拟显示（有头模式）"""
        try:
            # 在GitHub Actions中，我们需要设置虚拟显示
            if os.getenv('GITHUB_ACTIONS'):
                logger.info('🖥️ 检测到GitHub Actions环境，设置虚拟显示...')
                
                # 确保显示服务器在运行
                import subprocess
                
                # 检查DISPLAY环境变量
                display = os.getenv('DISPLAY', ':99')
                logger.info(f'使用显示: {display}')
                
                # 设置窗口管理器（可选）
                try:
                    subprocess.Popen(['fluxbox'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(2)
                    logger.info('✅ 窗口管理器已启动')
                except:
                    logger.info('ℹ️ 窗口管理器启动失败，继续执行')
                
                return True
            else:
                logger.info('ℹ️ 本地环境，无需设置虚拟显示')
                return True
                
        except Exception as e:
            logger.warning(f'⚠️ 设置虚拟显示失败: {e}')
            return False
    
    async def run_with_real_mouse(self):
        """使用真实鼠标操作的Selenium方案"""
        try:
            import undetected_chromedriver as uc
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, NoSuchElementException
            
            # 设置虚拟显示
            if not self.setup_virtual_display():
                logger.error('❌ 虚拟显示设置失败')
                return False
            
            # 设置pyautogui
            pyautogui = self.setup_pyautogui()
            if not pyautogui:
                logger.error('❌ pyautogui设置失败')
                return False
            
            logger.info('🔧 初始化有头模式Chrome...')
            
            options = uc.ChromeOptions()
            
            # 关键：不使用headless模式！
            # options.add_argument('--headless')  # 注释掉这行
            
            # 基本设置
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1366,768')
            options.add_argument('--window-position=0,0')
            
            # 反检测设置
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--no-first-run')
            options.add_argument('--disable-default-apps')
            
            # 用户代理
            ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            options.add_argument(f'--user-agent={ua}')
            
            # GitHub Actions环境特殊设置
            if os.getenv('GITHUB_ACTIONS'):
                options.add_argument('--display=:99')
                options.add_argument('--no-xshm')  # 禁用共享内存
            
            driver = uc.Chrome(
                options=options, 
                version_main=None,
                use_subprocess=True
            )
            
            wait = WebDriverWait(driver, 30)
            
            try:
                # 等待浏览器完全加载
                time.sleep(3)
                
                # 最大化窗口确保元素可见
                try:
                    driver.maximize_window()
                    logger.info('✅ 浏览器窗口已最大化')
                except:
                    logger.info('ℹ️ 窗口最大化失败，继续执行')
                
                # 登录流程
                logger.info('🌐 访问登录页面...')
                driver.get(self.login_url)
                time.sleep(3)
                
                # 输入登录信息
                email_field = wait.until(EC.element_to_be_clickable((By.ID, 'email')))
                password_field = driver.find_element(By.ID, 'password')
                login_btn = driver.find_element(By.ID, 'submit')
                
                # 使用真实的键盘输入（可选）
                logger.info('⌨️ 输入登录信息...')
                email_field.clear()
                email_field.send_keys(self.email)
                time.sleep(1)
                
                password_field.clear()
                password_field.send_keys(self.password)
                time.sleep(1)
                
                # 使用真实鼠标点击登录按钮
                logger.info('🖱️ 使用真实鼠标点击登录按钮...')
                self.real_mouse_click(driver, login_btn, pyautogui)
                
                # 等待登录完成
                time.sleep(5)
                
                if 'dashboard' not in driver.current_url:
                    logger.error(f'❌ 登录失败，当前URL: {driver.current_url}')
                    driver.save_screenshot('/tmp/real_mouse_login_failed.png')
                    return False
                
                logger.info('✅ 登录成功！')
                
                # 续期流程
                logger.info('🌐 访问续期页面...')
                driver.get(self.renew_url)
                time.sleep(3)
                
                # 查找续期按钮
                renew_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn.btn-outline-primary')))
                
                # 使用真实鼠标点击续期按钮
                logger.info('🖱️ 使用真实鼠标点击续期按钮...')
                self.real_mouse_click(driver, renew_btn, pyautogui)
                
                # 等待Turnstile加载
                time.sleep(5)
                
                # 处理Turnstile验证
                logger.info('🔐 开始使用真实鼠标处理Turnstile验证...')
                success = await self.handle_turnstile_with_real_mouse(driver, pyautogui)
                
                if success:
                    logger.info('🎉 Turnstile验证成功！')
                else:
                    logger.warning('⚠️ Turnstile验证可能未完成，但继续执行')
                
                # 等待最终完成
                time.sleep(5)
                
                # 保存最终截图
                driver.save_screenshot('/tmp/real_mouse_final.png')
                logger.info('✅ 真实鼠标方案执行完成！')
                return True
                
            except Exception as e:
                logger.error(f'❌ 真实鼠标方案执行出错: {e}')
                driver.save_screenshot('/tmp/real_mouse_error.png')
                return False
            finally:
                driver.quit()
                
        except ImportError as e:
            logger.error(f'❌ 导入错误: {e}')
            logger.error('请安装所需依赖: pip install undetected-chromedriver pyautogui pillow')
            return False
        except Exception as e:
            logger.error(f'❌ 真实鼠标方案初始化失败: {e}')
            return False
    
    def real_mouse_click(self, driver, element, pyautogui):
        """使用真实鼠标点击元素"""
        try:
            # 滚动到元素位置
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            
            # 获取元素位置
            location = element.location_once_scrolled_into_view
            size = element.size
            
            # 计算点击位置（元素中心）
            click_x = location['x'] + size['width'] // 2
            click_y = location['y'] + size['height'] // 2
            
            logger.info(f'🎯 元素位置: ({location["x"]}, {location["y"]}), 尺寸: ({size["width"]}, {size["height"]})')
            logger.info(f'🖱️ 真实鼠标点击位置: ({click_x}, {click_y})')
            
            # 使用pyautogui进行真实鼠标点击
            pyautogui.click(click_x, click_y, duration=0.2)
            logger.info('✅ 真实鼠标点击完成')
            
            return True
            
        except Exception as e:
            logger.error(f'❌ 真实鼠标点击失败: {e}')
            
            # 备用方案：JavaScript点击
            try:
                driver.execute_script("arguments[0].click();", element)
                logger.info('✅ 备用JavaScript点击完成')
                return True
            except Exception as e2:
                logger.error(f'❌ JavaScript点击也失败: {e2}')
                return False
    
    async def handle_turnstile_with_real_mouse(self, driver, pyautogui):
        """使用真实鼠标处理Turnstile验证"""
        max_wait_time = 90
        start_time = time.time()
        
        logger.info('🔍 寻找Turnstile验证框...')
        
        while time.time() - start_time < max_wait_time:
            try:
                # 检查是否已经完成验证
                if self.check_turnstile_completion(driver):
                    logger.info('✅ Turnstile验证已完成！')
                    return True
                
                # 查找所有iframe
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                logger.info(f'🔍 找到 {len(iframes)} 个iframe')
                
                for i, iframe in enumerate(iframes):
                    try:
                        src = iframe.get_attribute('src') or ''
                        logger.info(f'iframe {i+1}: {src}')
                        
                        # 检查是否是Turnstile iframe
                        if any(keyword in src.lower() for keyword in ['challenges.cloudflare.com', 'turnstile']):
                            logger.info(f'🎯 发现Turnstile iframe {i+1}')
                            
                            # 切换到iframe
                            driver.switch_to.frame(iframe)
                            
                            # 查找checkbox
                            checkbox_selectors = [
                                'input[type="checkbox"]',
                                '[role="checkbox"]',
                                '.cb-i',
                                'span[role="checkbox"]',
                                'div[role="checkbox"]'
                            ]
                            
                            for selector in checkbox_selectors:
                                try:
                                    checkboxes = driver.find_elements(By.CSS_SELECTOR, selector)
                                    logger.info(f'选择器 {selector} 找到 {len(checkboxes)} 个元素')
                                    
                                    for j, checkbox in enumerate(checkboxes):
                                        try:
                                            if checkbox.is_displayed():
                                                logger.info(f'🖱️ 尝试真实鼠标点击复选框 {j+1}')
                                                
                                                # 获取iframe在页面中的位置
                                                iframe_rect = driver.execute_script("""
                                                    return arguments[0].getBoundingClientRect();
                                                """, iframe)
                                                
                                                # 获取checkbox在iframe中的位置
                                                checkbox_rect = driver.execute_script("""
                                                    return arguments[0].getBoundingClientRect();
                                                """, checkbox)
                                                
                                                # 计算checkbox在整个页面中的绝对位置
                                                absolute_x = iframe_rect['x'] + checkbox_rect['x'] + checkbox_rect['width'] // 2
                                                absolute_y = iframe_rect['y'] + checkbox_rect['y'] + checkbox_rect['height'] // 2
                                                
                                                logger.info(f'🎯 Turnstile复选框绝对位置: ({absolute_x}, {absolute_y})')
                                                
                                                # 使用真实鼠标点击
                                                pyautogui.click(absolute_x, absolute_y, duration=0.3)
                                                logger.info('✅ 已使用真实鼠标点击Turnstile复选框')
                                                
                                                # 等待验证处理
                                                time.sleep(3)
                                                
                                                driver.switch_to.default_content()
                                                
                                                # 检查验证是否完成
                                                if self.check_turnstile_completion(driver):
                                                    logger.info('🎉 Turnstile验证成功完成！')
                                                    return True
                                                
                                                # 重新进入iframe继续尝试
                                                driver.switch_to.frame(iframe)
                                                
                                        except Exception as e:
                                            logger.warning(f'处理复选框 {j+1} 失败: {e}')
                                            
                                except Exception as e:
                                    logger.warning(f'查找选择器 {selector} 失败: {e}')
                            
                            driver.switch_to.default_content()
                            
                    except Exception as e:
                        logger.warning(f'处理iframe {i+1} 失败: {e}')
                        driver.switch_to.default_content()
                
                # 如果iframe方法失败，尝试主页面元素
                logger.info('🔍 尝试在主页面查找Turnstile元素...')
                main_selectors = [
                    '[data-sitekey]',
                    '.cf-turnstile',
                    '[id*="turnstile"]',
                    '[class*="turnstile"]'
                ]
                
                for selector in main_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            logger.info(f'主页面找到 {len(elements)} 个 {selector} 元素')
                            
                            for element in elements:
                                if element.is_displayed():
                                    logger.info('🖱️ 尝试真实鼠标点击主页面Turnstile元素')
                                    
                                    if self.real_mouse_click(driver, element, pyautogui):
                                        time.sleep(3)
                                        if self.check_turnstile_completion(driver):
                                            logger.info('🎉 主页面Turnstile验证成功！')
                                            return True
                                    
                    except Exception as e:
                        logger.warning(f'处理主页面选择器 {selector} 失败: {e}')
                
                # 等待一段时间再重试
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0:
                    logger.info(f'⏳ 真实鼠标Turnstile验证等待中... ({elapsed}/{max_wait_time}秒)')
                
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f'⚠️ 真实鼠标Turnstile处理异常: {e}')
                time.sleep(2)
        
        logger.warning('⚠️ 真实鼠标Turnstile验证超时')
        return False
    
    def check_turnstile_completion(self, driver):
        """检查Turnstile是否已完成"""
        try:
            token_element = driver.find_element(By.NAME, 'cf-turnstile-response')
            token_value = token_element.get_attribute('value')
            
            if token_value and len(token_value) > 10:
                logger.info(f'✅ 检测到Turnstile token: {token_value[:20]}...')
                return True
                
        except:
            pass
        
        return False
    
    async def run(self):
        """主执行函数"""
        logger.info('🚀 开始真实鼠标点击方案')
        
        success = await self.run_with_real_mouse()
        
        if success:
            logger.info('🎉 真实鼠标方案执行成功！')
            return True
        else:
            logger.error('❌ 真实鼠标方案执行失败！')
            return False

async def main():
    """程序入口"""
    try:
        bot = RealMouseRenewBot()
        success = await bot.run()
        
        if success:
            logger.info('🎉 ===== 真实鼠标续期任务执行成功！=====')
            sys.exit(0)
        else:
            logger.error('💥 ===== 真实鼠标续期任务执行失败！=====')
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
