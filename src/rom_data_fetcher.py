import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from lineage_os import LineageOS


class ROMDataFetcher:
    def fetch_device_info(self, channel):
        if channel == "Google Play Services":
            url = "https://developers.google.com/android/images"
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)

            acknowledge_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'devsite-acknowledgement-link')]"))
            )
            acknowledge_button.click()

            headers = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//h2[contains(text(), 'for Pixel')]"))
            )

            device_data = []

            for header in headers:
                device_name = header.text.split("for ")[1]
                code_name = header.get_attribute("id")

                table = header.find_element(By.XPATH, "./following-sibling::div[@class='devsite-table-wrapper']//table")
                rows = table.find_elements(By.XPATH, ".//tbody/tr")
                for row in rows:
                    version = row.find_element(By.XPATH, "./td[1]").text
                    link_elements = row.find_elements(By.XPATH, "./td[3]/a")
                    if link_elements:
                        link = link_elements[0].get_attribute("href")
                    else:
                        link = "N/A"

                    device_data.append({
                        "device_name": device_name,
                        "code_name": code_name,
                        "version": version,
                        "link": link
                    })

            driver.quit()
            return device_data
        
        elif channel in ["GrapheneOS", "GrapheneOSBeta"]:
            url = "https://grapheneos.org/releases"
            options = uc.ChromeOptions()
            options.add_argument("--headless=new")
            driver = uc.Chrome(options=options)
            driver.get(url)

            section_id = "stable-channel" if channel == "GrapheneOS" else "beta-channel"
            section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, section_id))
            )

            device_data = []

            for device in section.find_elements(By.XPATH, ".//h3"):
                device_name = device.text.strip()
                code_name = device.find_element(By.XPATH, ".//a").get_attribute("href").split("#")[1].split("-")[0]

                version_element = device.find_element(By.XPATH, "./following-sibling::p[1]/a")
                version = version_element.text.strip()

                factory_link = device.find_element(By.XPATH, "./following-sibling::ul[1]/li[1]/a").get_attribute("href")

                device_data.append({
                    "device_name": device_name,
                    "code_name": code_name,
                    "version": version,
                    "link": factory_link,
                    "sha256_checksum": "N/A"
                })

            driver.quit()
            return device_data

        elif channel == "LineageOS":
            device_data = []
            for device_code_name, device_info in LineageOS.additional_partitions.items():
                url = f"https://download.lineageos.org/devices/{device_code_name}/builds"
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                driver = webdriver.Chrome(options=options)
                driver.get(url)

                build_divs = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".border-b.border-solid.border-black.border-opacity-15"))
                )

                for build_div in build_divs:
                    file_divs = build_div.find_elements(By.CSS_SELECTOR, ".downloadable")
                    if file_divs:
                        file_name = file_divs[0].find_element(By.CSS_SELECTOR, ".title").text.strip()
                        version = file_name.split("-")[2]
                        file_links = {}

                        for file_div in file_divs:
                            file_name = file_div.find_element(By.CSS_SELECTOR, ".title").text.strip()
                            file_link = file_div.find_element(By.TAG_NAME, "a").get_attribute("href")
                            file_links[file_name] = file_link

                        device_files = {}
                        for file_name in device_info["files"]:
                            if file_name in file_links:
                                device_files[file_name] = file_links[file_name]

                        device_name = device_info["device_name"].replace("Google ", "")

                        device_data.append({
                            "device_name": device_name,
                            "code_name": device_code_name,
                            "version": version,
                            "files": device_files
                        })

                driver.quit()
            return device_data    
            
        else:
            return []
