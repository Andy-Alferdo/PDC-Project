This code uses Beautiful soup to scrapes image, name and the price of the product on the product pages using both parallel processing and sequential processing.
It starts by first getting the links (you can add the links in the code or make a txt file and provide it when running the code). it accessing the links by using request library.
After accessing the links it copies the html of the page to a temporary text file using beautiful soup, this makes it easier to extract details of the product.
Now this is where errors can occurs, the reason being the code searches for the classes of the image, name and price. But not every e-commerce site has the same classes so the classes in the code needs to be edited according to the e-commerce website, the classes i have put in works for Alibaba.
If you want to add support for any other website you need to check the classes in the product page and edit the classes in the code accordingly.
After getting all the details it saves the image in a separate folder where the code is stored and saves the name , price and the location of the image in an csv file.
This is all the internal working, for the display i used tinker. You can copy the link from the code to a text file or provide your own. After providing the txt file you click sequential or parallel extraction. It also shows how much time it took for the extraction.
