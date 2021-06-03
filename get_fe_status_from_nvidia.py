#Script to check nvidia's website for changes in the URL of the FE cards. Region-specific, this one is targeted at ldlc and nbb. CHoose your store in the nvidia.yml

import requests
from datetime import datetime
import yaml
import asyncio
import webbrowser
from fake_useragent import UserAgent
import sys
import time

# Remember to use your own values from my.telegram.org and set them in the config.json file!
with open("nvidia.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

#Random variables
channel_name = 'NvidiaStore'
chosenstore = cfg['yourstore']
ua = UserAgent()

#Preparing class and objects for the monitoring
class cards:
    def __init__(self, cardname, cardsku, oldretailerlink, newretailerlink):
        self.cardname = cardname
        self.cardsku = cardsku
        self.oldretailerlink = oldretailerlink
        self.newretailerlink = newretailerlink
#Different code depending on whether the user has chosen ldlc or nbb
if chosenstore == 'ldlc':
    card3090ti = cards(cfg['card3090ti']['name'], cfg['card3090ti']['sku'], "", "")
    card3090 = cards(cfg['card3090']['name'], cfg['card3090']['sku'], cfg['card3090']['ldlc']['oldurl'], "")
    card3080ti = cards(cfg['card3080ti']['name'], cfg['card3080ti']['sku'], "", "")
    card3080 = cards(cfg['card3080']['name'], cfg['card3080']['sku'], cfg['card3080']['ldlc']['oldurl'], "")
    card3070ti = cards(cfg['card3070ti']['name'], cfg['card3070ti']['sku'], "", "")
    card3070 = cards(cfg['card3070']['name'], cfg['card3070']['sku'], cfg['card3070']['ldlc']['oldurl'], "")
    card3060ti = cards(cfg['card3060ti']['name'], cfg['card3060ti']['sku'], cfg['card3060ti']['ldlc']['oldurl'], "")
    retailerurl = 'https://www.ldlc.com'
    sitelocale = "fr-fr"
elif chosenstore == 'nbb':
    card3090ti = cards(cfg['card3090ti']['name'], cfg['card3090ti']['sku'], "", "")
    card3090 = cards(cfg['card3090']['name'], cfg['card3090']['sku'], cfg['card3090']['nbb']['oldurl'], "")
    card3080ti = cards(cfg['card3080ti']['name'], cfg['card3080ti']['sku'], "", "")
    card3080 = cards(cfg['card3080']['name'], cfg['card3080']['sku'], cfg['card3080']['nbb']['oldurl'], "")
    card3070ti = cards(cfg['card3070ti']['name'], cfg['card3070ti']['sku'], "", "")
    card3070 = cards(cfg['card3070']['name'], cfg['card3070']['sku'], cfg['card3070']['nbb']['oldurl'], "")
    card3060ti = cards(cfg['card3060ti']['name'], cfg['card3060ti']['sku'], cfg['card3060ti']['nbb']['oldurl'], "")
    retailerurl = 'https://www.notebooksbilliger.de'
    sitelocale = "de-de"
else:
    print('Please fill the yourstore variable with either ldlc or nbb')
    raise SystemExit(0)

#Update the targetgpus variable with the cards you want to monitor
targetgpus = [card3090ti, card3090, card3080ti, card3080, card3070ti, card3070, card3060ti]

def print_time(*content):
    """
    Can be used as a normal print function but includes the current date and time
    enclosed in brackets in front of the printed content.
    :param content: The content you would normally put in a print() function
    """
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{date_time}] - [INFO] ", *content)


#Slimmed-down function to open links 
async def check_urls(urls, channel_name):
        webbrowser.open_new_tab(urls)
        print_time(f'Link opened from #{channel_name}: {urls}')

#Function to check the current store URLs on the nvidia website and return it back to the startloop function to check against the old ones
async def check_nvidia(targetgpus):
    browseragent = ua.random
    headers = {'User-Agent': browseragent}
    requesturl = "https://api.nvidia.partners/edge/product/search?page=1&limit=9&locale=" + sitelocale + "&category=GPU&manufacturer=NVIDIA&manufacturer_filter=NVIDIA~4"
    while True:
        try:
            searchedproducts = requests.get(requesturl, timeout=5, headers=headers).json()['searchedProducts']
            break
        except:
            print("Unexpected error:", sys.exc_info()[0])
            time.sleep(3)
    for targetgpu in targetgpus:
        if searchedproducts['featuredProduct']["productSKU"] == targetgpu.cardsku or searchedproducts['featuredProduct']["displayName"] == targetgpu.cardname:
            retailers = searchedproducts['featuredProduct']['retailers']
            for s in range(len(retailers)):
                if retailers[s]["retailerName"] == retailerurl:
                    targetgpu.newretailerlink = retailers[s]["purchaseLink"]
        retailers = searchedproducts['productDetails']
        for s in range(len(retailers)):
            if retailers[s]["productSKU"] == targetgpu.cardsku or retailers[s]["displayName"] == targetgpu.cardname:
                productretailers = retailers[s]['retailers']
                for s in range(len(productretailers)):
                    if productretailers[s]["retailerName"] == retailerurl:
                        targetgpu.newretailerlink = productretailers[s]["purchaseLink"]
    return targetgpus

#Function that loops around and checks if the new url is the same as the old url, and if not it opens the page in the browser then updates the main object of that gpu to avoid opening it twice
async def startloop():
    successes = []
    while True:
        results = await check_nvidia(targetgpus)
        for targetgpu in targetgpus:
            if targetgpu.oldretailerlink == targetgpu.newretailerlink:
                print_time("Nothing Changed for " + targetgpu.cardname)
            else:
                print(targetgpu.newretailerlink)
                await check_urls(targetgpu.newretailerlink, channel_name)
                targetgpu.oldretailerlink = targetgpu.newretailerlink
        await asyncio.sleep(2)

#Code to start and loop the function above
loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(startloop())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("Closing Loop")
    loop.close()