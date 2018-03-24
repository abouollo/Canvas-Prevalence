import bs4 as bs
import csv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import time, requests
#from urlparse import urljoin
from urllib.parse import urljoin
start_time = time.time()
import subprocess
from threading import Thread
def scrapefun(file_name):
    count1 = 0
    count = 0
    unread = 0
    list_website=0
    
    with open(file_name, ) as csvfile:
        CSVreader = csv.reader(csvfile, delimiter=',')
        

        #browser = webdriver.Firefox(executable_path=r'geckodriver.exe')
        #browser = webdriver.Chrome()

        for row in CSVreader:

            try:
                browser = webdriver.Firefox(executable_path=r'geckodriver.exe')
                #browser = webdriver.Chrome()

                
                trc = 0
                site = "http://"+ row[1]

                list_website+=1
                file1 = open("URLs_Attempted_But_Failed.txt", "a+")
                file2 = open("URLS_Attempted_and_Successfully_Read.txt", "a+")
                file3 = open("URLS_Read_and_Contain_Canvas.txt", "a+")
                file4 = open("Entire_List_of_URLs_Attempted.txt", "a+")
                file5 = open("Statistics.txt", "w+")
                file4.write(site + '\n')
                file4.close()

                print(site)
                browser.set_page_load_timeout(60)
                try:
                    browser.get(site)
                except TimeoutException as e:
                    print(e)
                    print("Error Reading")
                    file1.write(site+'\n')
                    file1.close()
                    unread += 1
                    browser.quit()
                    continue
                try:
                    alert = browser.switch_to.alert
                    alert.accept()
                    browser.switch_to.default_content()
                except:
                    browser.switch_to.default_content()


            except Exception as e:
                print(e)
                print("Error Reading")
                file1.write(site+'\n')
                file1.close()
                unread += 1
                browser.quit()
                continue
            
            try:
                
                source = browser.page_source
                soup = bs.BeautifulSoup(source, "lxml")
                file2.write(site + '\n')
                file2.close()
                count1+=1
                if (soup.find_all('canvas')):
                    count += 1
                    trc = 1
                    file3.write(site + '\n')
                    file3.close()
                
                # entering this part if the canvas tag is not found in the html source
                
                if trc == 0:

                    # checking if canvas tag createcanvas function is present in the script tags in the main source

                    r = check_source(browser.current_url, soup)
                    if r == 1:
                        count+=1
                        file3.write(site + '\n')
                        file3.close()

                        #if found in script tag the createcanvas method then increment
                        # save to file and continue
                        browser.quit()

                        continue


                    #come to this part if and only if not found canvas tag in source and 
                    # createcanvas method is not found in scrpt tags as source

                            
                    for attr in browser.find_elements_by_tag_name("iframe"):

                        #going throgh alll th iframes
                        
                        if trc == 0:
                            try:
                                t=browser.switch_to.frame(attr)
                                
                                try:
                                    #creating a new soup to pass in the method
                                    soup = bs.BeautifulSoup(browser.page_source, "html.parser")


                                    # passing to the function to check for createcanvas method in the script tags
                                    
                                    r = check_source(browser.current_url, soup)

                                    # if 1 is returned then createcanvas method is found in the script tags
                                    if r == 1:
                                        # in that case increment count 
                                        # write to file
                                        #break the loop
                                        count += 1
                                        file3.write(site + '\n')
                                        file3.close()
                                        break
                                except Exception as e:
                                    print(e)

                                # otherwise come to this part and handle exception line by line
                                
                                t=browser.find_element_by_tag_name('canvas')
                                trc = 1
                                
                                count += 1
                                file3.write(site + '\n')
                                file3.close()

                                browser.switch_to.default_content()
                            except Exception as e:
                                browser.switch_to.default_content()
                    try:
                        browser.quit() 
                    except:
                        pass
                try:
                    browser.quit()
                except:
                    pass

            
            except Exception as e:
                print(e)
                print("Error Reading")
                file1.write(site+'\n')
                file1.close()
                unread += 1
                try:
                    browser.quit()
                except:
                    pass
            try:
                browser.quit()
            except:
                pass                 
        
        try:
            percentage_calc=(count/count1)*100
        except:
            pass
       

        file5.write("Total Websites read attempt: " + str(list_website) + '\n')
        file5.write("Websites succesfully read: " + str(count1) + '\n')
        file5.write("Website having canvas: " + str(count) + '\n')
        file5.write("Websites failed read: " + str(unread) + '\n')
        file5.write("Percentage of websites having canvas: "+str(percentage_calc) + '\n')
        file5.close()

    print("count" , count)
    print("unread" , unread)
    return(count,unread)

def check_source(root, soup):

    # setting flag to 0 initially
    trc = 0

    # if createcanvas method found in the script tags as text directly embedded

    if 'createElement("canvas")' in str(soup.text.encode('utf8')) or "createElement('canvas')" in str(soup.text.encode('utf8')):
        trc = 1
        # in that case set trc to 1 


    # if trc is 0 means that not found in the initial script text portion directly embedded

    if trc == 0:
        # javascript not in the script as text but as src links so getting all the src links
        srclist = [l.get('src') for l in soup.find_all('script') if l.get('src')]


        # for each src link

        for l in srclist:
            

            if trc == 0:

                try:
                    # visit te src link
                    resp = requests.get(urljoin(root, l))

                    # make soup of the remote javascript source

                    soup = bs.BeautifulSoup(resp.content, 'html.parser')

                    # then try to find on each src source

                    if 'createElement("canvas")' in str(soup.text.encode('utf8')) or "createElement('canvas')" in str(soup.text.encode('utf8')):
                        # if yes then make trc to 1
                        trc = 1
                except Exception as e:
                    pass
        
    # alas if trc is 1 then return 1 
    if trc == 1:
        return 1

    # else return 0
    else:
        return 0

if __name__ == '__main__':

    scrapefun("top-sites.csv")
    print("--- %s seconds are taken for execution---" % (time.time() - start_time))
