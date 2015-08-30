#!/usr/bin/python3
import time
import datetime
import os

from selenium import webdriver
from selenium.webdriver.common.by import By

from tkinter import *
import tkinter

import threading
import subprocess

class File:

	name = None
	header = None

	def __init__(self):
		self.name = "Companies-Data.csv"
		self.header = "Company,Industry,First Name,Last Name,Email,Title,Address,Tel,Fax,Website,General Email\n"

	def generate_file(self, output_data_referral, output_data_normal, log_text, file_name=None):
		if file_name is not None:
			FORMAT = '%Y%m%d%H%M%S'
			self.name_referral = file_name + '-' + datetime.datetime.now().strftime(FORMAT) + '-Referral.csv' 
			self.name_normal = file_name + '-' + datetime.datetime.now().strftime(FORMAT) + '-Normal.csv' 

		output_file_referral = open(os.path.expanduser("~/Desktop/") + self.name_referral, 'w')
		output_file_normal = open(os.path.expanduser("~/Desktop/") + self.name_normal, 'w')
		
		output_file_referral.write(self.header)
		output_file_normal.write(self.header)

		for line in output_data_referral:
			output_file_referral.write(line)

		for line in output_data_normal:
			output_file_normal.write(line)

		output_file_referral.close()
		output_file_normal.close()

		if len(output_data_referral) > 0:
			log_text.insert(END, "File -> " + self.name_referral + " created successfully!\n")
			log_text.yview(END)

		if len(output_data_normal) > 0:
			log_text.insert(END, "File -> " + self.name_normal + " created successfully!\n")
			log_text.yview(END)

class RedbooksExtractor:

	driver = None
	username = None
	password = None
	debug = True
	secure_time = 0

	def __init__(self):

		if self.driver != None:
			self.driver.close()
			self.driver = None

		self.username = ""
		self.password = ""

		if self.debug == True:
			self.driver=webdriver.Firefox()
		else:
			phantomjs_path = os.path.dirname(os.path.realpath(__file__)) + "/phantomjs"
			self.driver=webdriver.PhantomJS(executable_path=phantomjs_path, service_log_path=os.path.devnull)

		self.driver.implicitly_wait(30)
		self.driver.get('http://www.redbooks.com')

		# Login
		# Click on the SIGN IN button
		self.driver.find_element_by_xpath('/html/body/div/div/div[1]/div/ul/li[1]/a').click()

		# Fill up login information 
		emailCred=self.driver.find_element_by_id('emailId')
		emailCred.send_keys(self.username)
		pwd=self.driver.find_element_by_id('password')
		pwd.send_keys(self.password)

		# Click on the login button
		signInBtn = self.driver.find_element_by_id('signInButton').click()

		try:
			# Check if login was successful
			self.driver.find_element_by_class_name('welcome') 
		except:
			self.driver.close()
			self.driver = None
			self.__init__()
			
	def set_secure_mode(self):
		self.secure_time = 15

	def go_to_adv_filter(self):
		# Click the Redbooks logo
		self.driver.find_element_by_id('logo').click()

		# Advanced search
		self.driver.find_element_by_xpath('/html/body/div[1]/div/form[1]/div/div[2]/div/div[1]/div[1]/div[1]/div[3]/a').click()

	def get_industries_adv_filter(self, field):

		fields = self.driver.find_element_by_id('field1')
		for option in fields.find_elements_by_tag_name('option'):
			if option.text == field:
				option.click()
				time.sleep(5 + self.secure_time)
				break

		industries = []

		values = self.driver.find_element_by_id('values1')
		for option in values.find_elements_by_tag_name('option'):
			industries.append(option.text)

		return industries


	def get_company_names_adv_filter(self, industry, limit, log):

		# Set query limit
		company_limit = 0
		try: 
			limit = int(limit)
		except:
			limit = 9999999

		try:
			values = self.driver.find_element_by_id('values1')
			for option in values.find_elements_by_tag_name('option'):
				if option.text == industry:
					option.click()
					time.sleep(10 + self.secure_time)
					break

			self.driver.find_element_by_id('advSubmit').click()

			self.driver.execute_script("searchAgain('999999')")
			
			time.sleep(30 + self.secure_time)

			companies = []
			companies_arr = self.driver.find_element_by_id('searchResults').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')

			if limit == 9999999:		
				log.insert(END, "Total of " + str(len(companies_arr)) + " companies to be queried:\n")		
			else:		
				log.insert(END, "Total of " + str(limit) + " companies to be queried:\n")		
			log.yview(END)

			for company in companies_arr:
				if company_limit == limit:
					break

				company_limit = company_limit + 1
				company_name = company.find_elements_by_tag_name('td')[2].find_element_by_tag_name('div').find_element_by_tag_name('a').text
				companies.append(company_name)

				log.insert(END, company_name+"\n")
				log.yview(END)

			log.insert(END, "-----------------------\n")
			log.yview(END)

			return companies

		except:
			log.insert(END, "Unable to get company list\n")
			log.yview(END)

	def get_all_agencie_companies(self, limit, log):		
		# Set query limit		
		company_limit = 0		
		try: 		
			limit = int(limit)		
		except:		
			limit = 9999999		
		try:		
			# Click the Redbooks logo		
			self.driver.find_element_by_id('logo').click()		
			time.sleep(3)

			# Click all agencies		
			self.driver.find_element_by_class_name('browse').find_elements_by_tag_name('a')[0].click()		
			self.driver.execute_script("searchAgain('9999999')")		
			time.sleep(30)		
			table = self.driver.find_element_by_id('searchResults').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')		
			if limit == 9999999:		
				log.insert(END, "Total of: " + str(len(table)) + " companies to be queried:\n")		
			else:		
				log.insert(END, "Total of: " + str(limit) + " companies to be queried:\n")		
			log.yview(END)		
			companies = []		
			for row in table:		
				if company_limit == limit:		
					break		
				company_limit = company_limit + 1		
				company_name = row.find_elements_by_tag_name('td')[2].find_element_by_tag_name('div').find_element_by_tag_name('a').text		
				companies.append(company_name)		
				log.insert(END, company_name+"\n")		
				log.yview(END)		
			log.insert(END, "-----------------------\n")		
			log.yview(END)		
			return companies		
		except:		
			log.insert(END, "Unable to get company list\n")		
			log.yview(END)		


	def has_keywords(self, keywords, title_keyphase):
		has_keyword = False
		for keyword in keywords:
			if ' ' in keyword:
				if keyword in title_keyphase:
					has_keyword = True
				else:
					has_keyword = False
			else:
				for title_word in title_keyphase.split(' '):
					if title_word == keyword: 
						has_keyword = True
						break
					else:
						has_keyword = False
									
				if has_keyword == True:
					break

		return has_keyword


	def find_companies_data(self, companies, keywords, referral_keywords, log):

		output_data_referral = []
		output_data_normal = []

		companies_size = len(companies)
		counter = 1
		i = 0
		clear = 50
		refresh = False

		while i >= 0 and i < companies_size:

			if (i != 0 and i % clear == 0) or refresh == True:
				log.insert(END, "Refreshing session. Wait...\n")
				log.yview(END)
				self.__init__()
				refresh = False

			company_name = companies[i];
			log.insert(END, "Company: " + company_name + ", number: " + str(counter) + " of " + str(companies_size) +"\n")
			log.yview(END)

			company_name = company_name.strip()
			
			try: 
				self.driver.find_element_by_id('logo').click()
				if i == 0:
					time.sleep(10)
				searchBox = self.driver.find_element_by_id('dashSearchInputBox')
				searchBox.clear()
				searchBox.send_keys(company_name)

				self.driver.find_element_by_id('searchButton').click()	
				if i == 0:
					time.sleep(10)			

				company = self.driver.find_element_by_xpath('/html/body/div[4]/div/div[6]/form/div/div[2]/table/tbody/tr/td[3]/div/a').click()
				if i == 0:
					time.sleep(10)
				company_info = self.driver.find_element_by_class_name('address').text.split('\n')
			except:
				try:
					self.driver.execute_script("dispAdvertiser()")		
					time.sleep(10)

					company = self.driver.find_element_by_xpath('/html/body/div[4]/div/div[6]/form/div/div[2]/table/tbody/tr/td[3]/div/a').click()
					if i == 0:
						time.sleep(10)
					company_info = self.driver.find_element_by_class_name('address').text.split('\n')
				except:
					refresh = True
					continue
			
			try:
				industry = self.driver.find_element_by_class_name('compnyType').text
			except:
				industry = "None"

			try: 
				address = company_info[0].split(':')[1].strip().replace(',','-')
			except:
				address = "None"
				
			try:
				tel = company_info[1].split(':')[1].strip().replace(',','-')
			except:
				tel = "None"

			try:
				fax = company_info[2].split(':')[1].strip().replace(',','-')
			except:
				fax = "None"

			try:
				website = company_info[3].split(':')[1].strip().replace(',','-')
			except:
				website = "None"

			try:
				general_email = company_info[4].split(':')[1].strip().replace(',','-')
			except:
				general_email = "None"

			# Get child companies
			try:
				self.driver.execute_script("showPage('corporatefamily', '1', '1000')")

				childs_table = self.driver.find_element_by_id('corporatefamilyTbl').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')

				for row in childs_table:
					row_detail = row.find_elements_by_tag_name('td')
					try:
						child_company_name = row_detail[1].find_element_by_tag_name('a').text
					except:
						break;

					if child_company_name not in companies:
						log.insert(END,'Adding company branch: ' + child_company_name + "\n")
						log.yview(END)	
						companies.append(child_company_name)

				companies_size = len(companies)
			except:
				companies_size = len(companies)
				pass


			try:
				self.driver.find_element_by_id('cinfo').click()
			except:
				log.insert(END, "Company: " + company_name + " does not have contacts available!\n")
				log.yview(END)
				i = i + 1
				counter = counter + 1
				refresh = True
				continue
			
			try:
				table = self.driver.find_element_by_id('contactTbl').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
			
				j = 0
				company_name = company_name.replace(',', '-')
				table_size = str(len(table))
				for row in table:
					j = j + 1
					row_detail = row.find_elements_by_tag_name('td')

					try:
						name = row_detail[2].text.split('\n')[0]
						fname = name.split(' ',1)[0]
						lname = name.split(' ',1)[1]
					except:
						fname = row_detail[2].text
						lname = "None"

					email = row_detail[2].find_element_by_tag_name('a').text
					title = row_detail[3].text.replace(',', '-').replace('\n', ' ')
					
					# Remove entries in the keywords input
					title_keyphase = title.lower().replace('-','').replace('\r', '').replace('\n', '').strip()
					invalid_professional = self.has_keywords(keywords, title_keyphase)

					log.insert(END,'Loading: ' + fname + ', number: ' + str(j) + ' from ' + table_size + ', company: ' + company_name+"\n")
					log.yview(END)		

					if email and not invalid_professional:
						if self.has_keywords(referral_keywords, title_keyphase):
							output_data_referral.append("{},{},{},{},{},{},{},{},{},{},{}\n".format(company_name, industry, fname, lname, email, title, address, tel, fax, website, general_email))
						else:
							output_data_normal.append("{},{},{},{},{},{},{},{},{},{},{}\n".format(company_name, industry, fname, lname, email, title, address, tel, fax, website, general_email))
					
			except:
				refresh = True
				continue

			log.insert(END, "-----------------------\n")
			log.yview(END)
			i = i + 1
			counter = counter + 1

		return (output_data_referral, output_data_normal)
		
	def destroy(self):
		self.driver.close()


class Interface(Frame):

	left_align = 20
	left_align_field = 130

	def __init__(self, parent):

		Frame.__init__(self, parent) 

		self.redbooks_extractor = RedbooksExtractor()
         
		self.parent = parent
		self.fields = ['Industry Focus (Agy only)', 'Industry Group (Adv only)']

		# Open Adv filter page
		self.redbooks_extractor.go_to_adv_filter()
		self.industries = self.redbooks_extractor.get_industries_adv_filter(self.fields[0])

		self.initUI()

	def initUI(self):
      
		self.parent.title("Redbooks Scraper")

		self.pack(fill=BOTH, expand=1)
		self.center_window()

		self.field_agy_checkbox()
		self.field_secure_mode_checkbox()
		self.field_dropdown()
		self.industry_dropdown()
		self.limit_text()
		self.companies_text()
		self.keywords_text()
		self.field_keywords_checkbox()
		self.referral_keywords_text()
		self.field_referral_keywords_checkbox()

		self.quit_button()
		self.csv_button()

		self.log_text()
    
	def center_window(self):
      
		self.width = 600
		self.heigth = 700

		sw = self.parent.winfo_screenwidth()
		sh = self.parent.winfo_screenheight()
        
		x = (sw - self.width)/2
		y = (sh - self.heigth)/2
		self.parent.geometry('%dx%d+%d+%d' % (self.width, self.heigth, x, y))

	def select_all_agy_checkbox(self):

		if self.field_agy_checkbox_val.get() == 1:
			self.companies_text.delete(1.0, END)
			self.companies_text.config(state='disabled')
			self.industry_dropdown.config(state='disabled')
		else:
			self.companies_text.config(state='normal')
			self.industry_dropdown.config(state='normal')

	def field_agy_checkbox(self):

		self.field_agy_checkbox_val = IntVar()
		self.field_agy_checkbox_val.set(1)

		self.field_agy_checkbox = Checkbutton(self, text="All agencies", variable=self.field_agy_checkbox_val, command=self.select_all_agy_checkbox)
		self.field_agy_checkbox.place(x=self.left_align+350, y=30)

	def field_secure_mode_checkbox(self):

		self.field_secure_mode_checkbox_val = IntVar()
		self.field_secure_mode_checkbox_val.set(0)

		self.field_secure_mode_checkbox = Checkbutton(self, text="Secure mode", variable=self.field_secure_mode_checkbox_val)
		self.field_secure_mode_checkbox.place(x=self.left_align+450, y=30)

	def field_label(self):

		self.field_label = Label(self, text="Field: ", font=("Helvetica", 18))
		self.field_label.place(x=self.left_align, y=30)

	def field_update(self, option):

		# Hide 'All agencies' checkbox
		if option != 'Industry Focus (Agy only)':
			self.companies_text.config(state='normal')
			self.industry_dropdown.config(state='normal')
			self.field_agy_checkbox_val.set(0)
			self.field_agy_checkbox.place(x=-350, y=30)
		else:
			self.companies_text.config(state='disabled')
			self.industry_dropdown.config(state='disabled')
			self.field_agy_checkbox_val.set(1)
			self.field_agy_checkbox.place(x=self.left_align+350, y=30)
			
		self.industries = self.redbooks_extractor.get_industries_adv_filter(option)

		self.industry_dropdown_default.set(self.industries[0])

		self.industry_dropdown['menu'].delete(0, "end")
		for industry in self.industries:
			self.industry_dropdown['menu'].add_command(label=industry, command=tkinter._setit(self.industry_dropdown_default, industry))

	def field_dropdown(self):

		self.field_label()

		self.field_dropdown_default = StringVar()
		self.field_dropdown_default.set(self.fields[0])

		self.field_dropdown = OptionMenu(self, self.field_dropdown_default, *self.fields, command=self.field_update)
		self.field_dropdown.config(bd=0, bg=None)
		self.field_dropdown.place(x=self.left_align+self.left_align_field, y=30)

	def industry_label(self):

		self.industry_label = Label(self, text="Industry: ", font=("Helvetica", 18))
		self.industry_label.place(x=self.left_align, y=80)

	def industry_dropdown(self):

		self.industry_label()

		self.industry_dropdown_default = StringVar()
		self.industry_dropdown_default.set(self.industries[0])

		self.industry_dropdown = OptionMenu(self, self.industry_dropdown_default, *self.industries)
		self.industry_dropdown.config(bd=0, bg=None, state='disabled')
		self.industry_dropdown.place(x=self.left_align+self.left_align_field, y=80)

	def limit_label(self):

		self.limit_label = Label(self, text="Limit: ", font=("Helvetica", 18))
		self.limit_label.place(x=self.left_align, y=130)

	def limit_text(self):

		self.limit_label()

		self.limit_text = Text(self, height=1, width=20)
		self.limit_text.config(bd=0, insertbackground="white", bg='black', fg="white", state='normal')
		self.limit_text.place(x=self.left_align+self.left_align_field, y=130)

	def companies_label(self):

		self.companies_label_details()

		self.companies_label = Label(self, text="Companies: ", font=("Helvetica", 18))
		self.companies_label.place(x=self.left_align, y=180)

	def companies_label_details(self):

		self.companies_label_details = Label(self, text="(separate by ';') ", font=("Helvetica", 12))
		self.companies_label_details.place(x=self.left_align, y=210)

	def companies_text(self):

		self.companies_label()

		self.companies_text = Text(self, height=4, width=50)
		self.companies_text.config(bd=0,  insertbackground="white", bg="black", fg="white", state='disabled')
		self.companies_text.place(x=self.left_align+self.left_align_field, y=180)

		self.companies_text.bind("<Key>", self.type_company)

	def type_company(self, key):
		companies = self.companies_text.get('0.0',END).strip()
		if len(companies) > 1:
			self.industry_dropdown.config(state='disabled')
			self.field_dropdown.config(state='disabled')
			self.field_agy_checkbox.config(state='disabled')
		else:
			self.industry_dropdown.config(state='normal')
			self.field_dropdown.config(state='normal')
			self.field_agy_checkbox.config(state='normal')

	def keywords_label(self):

		self.keywords_label_details()

		self.keywords_label = Label(self, text="Keywords: ", font=("Helvetica", 18))
		self.keywords_label.place(x=self.left_align, y=250)

	def keywords_label_details(self):

		self.keywords_label_details = Label(self, text="(separate by ';') ", font=("Helvetica", 12))
		self.keywords_label_details.place(x=self.left_align, y=280)

	def keywords_text(self):

		self.keywords_label()

		self.keywords_text = Text(self, height=4, width=50)
		self.keywords_text.config(bd=0, insertbackground="white", bg='black', fg="white")
		self.keywords_text.place(x=self.left_align+self.left_align_field, y=250)

	def select_keywords_checkbox(self):

		if self.field_keywords_checkbox_val.get() == 1:
			self.keywords_text.insert(END, "CFO;\nChief Financial Officer;\nHuman Resources;\nChairman;\nGeneral Counsel;\nTreasurer;\nController;\nFinance;\nTax;\nCopywriter;\nOperations;\nBudget;\nBilling;\nOffice Services;\nInvestment;\nSearch Engine;\nEnrollment;\nAcademic;\nCEO;\nCorporate Issues;\nAnalytics;\nModelling;\nCTO;\nChief Technology Officer;\nWriter;\nLeadership;\nSustainability;\nCitizenship;\nPrincipal;\nTechnology;\nRecruitment;\nTalent;\nPublic Affairs;\nGovernment;\nLegal;\nBusiness Intelligence;\nPractice;\nFinancial;\nStrategy;\nChief Strategy Officer;\nChief Talent Officer;\nTalent Acquisition;\nRetail Consultancy;\nStrategic Planning;\nCorporate Affairs;\nResearch;\nInvestor Relations;\nChief Operating Officer;\nExperience Planning;\nMedia Acquisition;\nPublic Relations;\nChief Revenue Officer;\nGroup Publisher;\nSales;\nLogistics;\nChief Commercial Officer;\nInsight;\nInformation Technology;\nMulticultural Strategy;\nConnections Planning;\nHuman Services;\nInternal Audit;\nManagement Supervisor;\nMedia Buyer;\nMedia Planner;\nOfficer Manager;\nTalent & Development;\nTrade Marketing;\nMedia Relations;\nProcurement;\nHome Care Division;\nStudio;\nPayable;\nAccountant;\nChief Recruitment Officer;\nChief Information Officer;\nPublisher;\nAudit;\nAdministration;\nChief Administrative Officer")
		else:
			self.keywords_text.delete(1.0, END)

	def field_keywords_checkbox(self):

		self.field_keywords_checkbox_val = IntVar()
		self.field_keywords_checkbox_val.set(0)

		self.field_keywords_checkbox = Checkbutton(self, text="Standard keywords", variable=self.field_keywords_checkbox_val, command=self.select_keywords_checkbox)
		self.field_keywords_checkbox.place(x=self.left_align+self.left_align_field, y=315)

	def referral_keywords_label(self):

		self.referral_keywords_label_details()

		self.referral_keywords_label = Label(self, text="Referral\nKeywords: ", font=("Helvetica", 18))
		self.referral_keywords_label.place(x=self.left_align, y=335)

	def referral_keywords_label_details(self):

		self.referral_keywords_label_details = Label(self, text="(separate by ';') ", font=("Helvetica", 12))
		self.referral_keywords_label_details.place(x=self.left_align, y=395)

	def referral_keywords_text(self):

		self.referral_keywords_label()

		self.referral_keywords_text = Text(self, height=4, width=50)
		self.referral_keywords_text.config(bd=0, insertbackground="white", bg='black', fg="white")
		self.referral_keywords_text.place(x=self.left_align+self.left_align_field, y=335)

	def select_referral_keywords_checkbox(self):

		if self.field_referral_keywords_checkbox_val.get() == 1:
			self.referral_keywords_text.insert(END, "VP;\nHead;\nPresident;\nFounder;\nVice;\nChief;\nExecutive;\nPartner;\nSVP")
		else:
			self.referral_keywords_text.delete(1.0, END)

	def field_referral_keywords_checkbox(self):

		self.field_referral_keywords_checkbox_val = IntVar()
		self.field_referral_keywords_checkbox_val.set(1)

		self.field_referral_keywords_checkbox = Checkbutton(self, text="Standard referral keywords", variable=self.field_referral_keywords_checkbox_val, command=self.select_referral_keywords_checkbox)
		self.field_referral_keywords_checkbox.place(x=self.left_align+self.left_align_field, y=405)

		# Set default values
		self.select_referral_keywords_checkbox()
  
	def csv_button(self):

		self.csv_button = Button(self, text="Generate CSV", command=self.generate_csv)
		self.csv_button.place(x=self.left_align, y=435)    

	def quit_button(self):

		self.quit_button = Button(self, text="Quit", command=self.close)
		self.quit_button.place(x=self.left_align+120, y=435)

	def log_label(self):

		self.log_label = Label(self, text="Log: ", font=("Helvetica", 18))
		self.log_label.place(x=self.left_align, y=465)

	def log_text(self):

		self.log_label()

		self.log_text = Text(self, height=8, width=80)
		self.log_text.config(bd=0, bg='black', fg="white", state='normal')
		self.log_text.place(x=self.left_align, y=505)

	def generate_csv(self):

		def callback():

			# Disable buttons
			self.quit_button.config(state='disabled')
			self.csv_button.config(state='disabled')

			output_data_referral = []
			output_data_normal = []
			companies = []
			file_name = "Companies"

			self.log_text.insert(END, "-----------------------\n")
			self.log_text.insert(END, "Start date: " + str(datetime.datetime.now())+"\n")
			self.log_text.insert(END, "-----------------------\n")
			self.log_text.yview(END)
			self.log_text.insert(END, "Companies to be queried:\n")
			self.log_text.yview(END)

			# Set secure mode
			if self.field_secure_mode_checkbox_val.get() == 1:
				self.redbooks_extractor.set_secure_mode()

			# Get companies list
			if self.field_dropdown_default.get() == 'Industry Focus (Agy only)' and self.field_agy_checkbox_val.get() == 1:
				file_name = self.field_dropdown_default.get() + '-AllAgencies'
				companies = self.redbooks_extractor.get_all_agencie_companies(self.limit_text.get('0.0',END).strip(), self.log_text)
			elif self.companies_text.get('0.0',END) and self.companies_text.get('0.0',END).isspace() == False:
				file_name = self.companies_text.get('0.0',END).replace('\n', '').replace('\r', '').strip().replace(';','-')
				companies = self.companies_text.get('0.0',END).replace('\n', '').replace('\r', '').strip().split(';')
				for company in companies:
					self.log_text.insert(END, company+"\n")
					self.log_text.yview(END)
			else:
				file_name = self.field_dropdown_default.get() + '-' + self.industry_dropdown_default.get()
				companies = self.redbooks_extractor.get_company_names_adv_filter(self.industry_dropdown_default.get(), self.limit_text.get('0.0',END).strip(), self.log_text)
			
			# Get keywords list
			keywords_phrase = self.keywords_text.get('0.0',END).lower().replace('\n', '').replace('\r', '').strip().split(';')
			keywords = []
			for phrase in keywords_phrase:
				keyword = phrase.strip()
				if keyword:
					keywords.append(keyword)

			# Get referral keywords list
			referral_keywords_phrase = self.referral_keywords_text.get('0.0',END).lower().replace('\n', '').replace('\r', '').strip().split(';')
			referral_keywords = []
			for phrase in referral_keywords_phrase:
				keyword = phrase.strip()
				if keyword:
					referral_keywords.append(keyword)

			output_data_referral, output_data_normal  = self.redbooks_extractor.find_companies_data(companies, keywords, referral_keywords, self.log_text)

			if len(output_data_referral) > 0 or len(output_data_normal) > 0:
				try:
					File().generate_file(output_data_referral, output_data_normal, self.log_text, file_name)
				except:
					self.log_text.insert(END,"Failed to create file -> " + file_name + "\n")
					self.log_text.yview(END)

			else:
				self.log_text.insert(END,"No companies found for this query!\n")
				self.log_text.yview(END)

			self.redbooks_extractor.go_to_adv_filter()

			# Enable buttons
			self.quit_button.config(state='normal')
			self.csv_button.config(state='normal')

			self.log_text.insert(END, "-----------------------\n")
			self.log_text.insert(END, "End date: " + str(datetime.datetime.now())+"\n")
			self.log_text.insert(END, "-----------------------\n")
			self.log_text.yview(END)

		t = threading.Thread(target=callback)
		t.start()

	def close(self):
		self.redbooks_extractor.destroy()
		self.quit()
		
def main():
  
	root = Tk()
	app = Interface(root)
	root.mainloop() 


main()
