import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import gspread
import time
import random as rd

# CLASES

class SeleniumDriver:

    def __init__(self, headless = False, driverPath = None):

        if driverPath != None:
            if headless:
                self.driver = get_driver_headless(driverPath)
            else:
                self.driver = get_driver_simple(driverPath)
        else:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())


    def get_driver_headless(self, driverPath):

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_experimental_option("prefs", {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True
            }) 
        options.add_argument('--window-size=1920,1080')  
        options.add_argument('--headless')

        return webdriver.Chrome(executable_path=driverPath,chrome_options=options)
    
    def get_driver_simple(self, driverPath):

        return webdriver.Chrome(executable_path=driverPath)


class Item:

    headers = 'Titulo;Precio;m2;Telefono;Descripcion;Link;Direccion;Observaciones;'

    def __init__(self, price, title, description, link, direction, phone, m2, observations):
        self.price = price
        self.title = title
        self.description = description
        self.link = link
        self.direction = direction
        self.phone = phone
        self.m2 = m2
        self.observations = observations
    
    def getcsvline(self):
        return cleanText(self.title) + ";" + cleanText(self.price) + ";" + cleanText(self.m2) + ";" + cleanText(self.phone) + "; " + cleanText(self.description) + " ;" + self.link + ";" + self.direction + ";" + self.observations + ";"
    
class Idealista:
    def __init__(self):
        pass

class Fotocasa:

    def __init__(self, start_url = 'https://www.fotocasa.es/es/alquiler/locales/madrid-capital/todas-las-zonas/l/1'):
        sel = SeleniumDriver()
        self.driver = sel.driver
        self.start_url = start_url
        self.items = []
        self.currentPage = 1
    
    def start(self):

        self.openurl(self.start_url)
        self.acceptCookies()
        while True:
            self.scrollDown()
            time.sleep(1)
            self.getItems()
            if self.isNextPage():
                self.currentPage += 1
                self.openurl(self.start_url.replace('/l/1', '/l/' + str(self.currentPage)))
                print('Page ' + str(self.currentPage) + ' ...')
            else:
                break
        
        print('')
        print('...Finished...')
        print('')
        
    def closeDriver(self):

        self.driver.close()

    def openurl(self,url):
        self.driver.get(url)
    
    def acceptCookies(self):
        button = self.driver.find_element_by_xpath("//*[@data-testid='TcfAccept']")
        button.click()
    
    def isNextPage(self):

        nextPage = None
        try:
            no_results = self.driver.find_element_by_class_name('re-SearchNoResults-title')
            nextPage = False
        except:
            nextPage = True

        return nextPage

    def scrollDown(self, times = 1):
        for n in range(40):
            self.driver.execute_script("window.scrollBy(0, 400)")

    def getItems(self):

        cardsElements = self.driver.find_elements_by_class_name("re-Card-secondary")

        for card in cardsElements:
            price, title, description, link, direction, tlf, m2, banos = '','','','','','','',''

            card_rows = card.text.split('\n')
            try:
                title = card.find_element_by_class_name('re-Card-title').text.replace('Local', 'Local ').replace(';',',')
            except:
                pass
            try:
                price = card.find_element_by_class_name('re-Card-price').text.replace('€ /mes','').replace(' ','').replace(';',',')
            except:
                pass

            try:
                features = card.find_element_by_class_name('re-CardFeatures-wrapper').text.replace(';',',')
            except:
                features = None
                pass
            
            if features != None:
                if 'baño' in features:
                    if 'baños' in features:
                        banos = features.split('baños')[0].replace(' ','') + ' baños'
                        m2 = features.split('baños')[1].split('m²')[0].replace(' ','')
                    else:
                        banos = features.split('baño')[0].replace(' ','') + ' baño'
                        m2 = features.split('baño')[1].split('m²')[0].replace(' ','')
                else:
                    banos = ''
                    try:
                        m2 = features.split(' m²')[0]
                    except:
                        pass
                
            try:
                description = card.find_element_by_class_name('re-Card-description').text.replace(';',',')
            except:
                pass  
            try:
                tlf = card.find_element_by_class_name('re-Card-contact').text.split('\n')[1].replace(' ','').replace(';',',')
            except:
                pass
            try:
                link = card.find_element_by_class_name('re-Card-link').get_attribute("href")
            except:
                pass
            try:
                direction = title.replace('Local ','').replace(';',',')
            except:
                pass
            
            if 'www.fotocasa.es' in link:
                newItem = Item(price, title, description, link, direction, tlf, m2, banos)
                self.items.append(newItem)

        print('Elements:',len(self.items))


class Belbex:

    def __init__(self, start_url = 'https://belbex.com/locales/madrid-provincia/alquiler/'):
        sel = SeleniumDriver()
        self.driver = sel.driver
        self.start_url = start_url
        self.items = []
        self.currentPage = 1
    
    def start(self):

        self.openurl(self.start_url)
        self.acceptCookies()
        while True:
            self.scrollDown()
            time.sleep(1)
            self.getItems()
            if self.isNextPage():
                self.currentPage += 1
                self.gotoNextPage()
                print('Page ' + str(self.currentPage) + ' ...')
            else:
                break
                
        print('')
        print('...Finished...')
        print('')
        
    def closeDriver(self):
        self.driver.close()

    def openurl(self,url):
        self.driver.get(url)
    
    def acceptCookies(self):
        button = self.driver.find_element_by_class_name("formbutton")
        button.click()
    
    def isNextPage(self):
        nextPage = None
        try:
            no_results = self.driver.find_element_by_xpath("//*[@aria-label='Página Siguiente']")
            nextPage = True
        except:
            nextPage = False

        return nextPage
    
    def gotoNextPage(self):
        self.driver.find_element_by_xpath("//*[@aria-label='Página Siguiente']").click()

    def scrollDown(self, times = 1):
        for n in range(40):
            self.driver.execute_script("window.scrollBy(0, 400)")

    def getItems(self):

        cardsElements = self.driver.find_elements_by_class_name("addressWrapper")

        for wrapper in cardsElements:

            card = wrapper.find_element_by_xpath('..')

            price, title, description, link, direction, tlf, m2, planta = '','','','','','','',''

            try:
                price = card.find_element_by_class_name('listingTotalPrice').text.replace('€/mes','').replace(' ','').replace(';',',')
            except:
                pass

            try:
                planta = card.find_element_by_class_name('listingFloorInfo').text
            except:
                pass

            try:
                m2 = card.find_element_by_class_name('listingSurface').text.replace(' m2','')
            except:
                pass
                
            try:
                link = card.find_element_by_class_name('listingAddress').get_attribute("href")
            except:
                pass
            try:
                city = card.find_element_by_class_name('listingCity').text
                strt = card.find_element_by_class_name('listingAddress').text
                direction = strt + city
                title = strt
            except:
                pass
            
            if 'belbex.com' in link:
                newItem = Item(price, title, description, link, direction, tlf, m2, planta)
                self.items.append(newItem)
                
        print('Elements:',len(self.items))


# HELPERS FUNCTIONS

def cleanText(string):
    string = string.replace('ñ','n')
    string = string.replace('á','a')
    string = string.replace('é','e')
    string = string.replace('í','i')
    string = string.replace('ó','o')
    string = string.replace('ú','u')
    string = string.replace('Á','A')
    string = string.replace('É','E')
    string = string.replace('Í','I')
    string = string.replace('Ó','O')
    string = string.replace('Ú','U')
    string = string.replace('"','')
    string = string.replace('-',' ')

    return string

def writeToCSV(filepath,items, headers = None):
    csv = open(filepath,"a")
    lines = []
    if headers != None:
        csv.write(headers + "\n")

    for item in items:
        line = (item.getcsvline())
        csv.write(line + "\n")
    
    csv.close()

def csvtovalues(filepath, separator = ';'):
    csvlines  = open(filepath, "r").readlines()
    values = []
    for line in csvlines:
        values.append(line.split(separator)[:-1])
    
    return values

def column(matrix, i):
    return [row[i] for row in matrix]

def without(array,i):
	return array[:i] + array[i+1:]

def filterExistingRows(rows):
    filt_rows = []
    links = column(table,3)
    for row in rows:
        if not (row[3] in links):
            filt_rows.append(row)
    return filt_rows

def isInRow(keyword,row):
    if keyword.lower() in row[0].lower() or keyword in row[2].lower():
        return True
    else:
        return False

def deleteDuplicates(filepath):
    csvread = open(filepath,"r")
    f = csvread.readlines()

    for i, line in enumerate(f):
        if line in without(f,i):
            f.pop(i)

    csvread.close()

    csvwrite = open(filepath,"w")
    csvwrite.writelines(f)

# MAIN PROGRAM

def main_fotocasa():
    fotocasa = Fotocasa()
    fotocasa.start()
    fotocasa.closeDriver()


    print('Elementos: '+ str(len(fotocasa.items)))

    writeToCSV('/Users/zeemarquez/Documents/Python/Pandas Corporate/WebScrapping/Datos/locales_fotocasa.csv', fotocasa.items, headers= Item.headers)

def main_belbex():
    belbex = Belbex()
    belbex.start()
    belbex.closeDriver()

    print('Elementos: '+ str(len(belbex.items)))

    writeToCSV('/Users/zeemarquez/Documents/Python/Pandas Corporate/WebScrapping/Datos/locales_belbex.csv', belbex.items, headers= Item.headers)
