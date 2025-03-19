#TERMINAL OUTPUT SETTINGS
#see alive_progress documentation for more info
#For progress bars
auto_bar = "classic"
#For loading bars
unknown_bar="waves"

#DATABASE SETTINGS
uri = "sqlite:////home/avasireddi3/projects/saroj_analytics/test.db"
table_name="test_listings"
xlsx_file_name="test_report"

#COLOR SCHEME SETTINGS
#colors in hexadecimal for table headings
colors_hex = {
            "zepto":{"text":"#f73563",
                     "bg":"#390067"},
            "instamart":{"text":"#f7f7f7",
                         "bg":"#f74f00"},
            "blinkit":{"text":"#2f8215",
                       "bg":"#f0c544"}
        }
colors_rgb = {
            "zepto":{"text":(247,53,99),
                     "bg":(57,0,103)},
            "instamart":{"text":(247,247,247),
                         "bg":(247,79,0)},
            "blinkit":{"text":(47,130,21),
                       "bg":(240,197,68)}
        }

#DATA PROCESSING
#similarity threshhold to match search query with product name (brand removed)
#any listing with a lower similarity threshold will be filtered out
similarity_threshold = 0.45

#REPORT GENERATION
#report title
report_title = "Vijay Ecommerce Pricing Report"
#title font settings
title_font = 'Helvetica'
title_font_size = 18
#margin on top, bottom, left and right
report_margins = 15
#if margin border should be included
margin_border=True
#table font settings
table_font = "Helvetica"
table_font_size = 7
#output pdf name
pdf_name="test"

#EMAIL GENERATION
#to email addresses
to = ["rohith@vijayfoods.com","aditya.vasireddi@gmail.com"]
#message content
msg_content = """Please find attached the report"""

#STORE LOCATOR
# max_lat = 13.176
# min_lat = 12.745
# min_long = 77.372
# max_long= 77.869
max_lat = 13.200
min_lat = 12.800
min_long = 77.400
max_long = 77.800
grid_detail = 3
