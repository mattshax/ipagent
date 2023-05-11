import pprint
import os
import sys
import html
import datetime
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

arg_filenames = ['data/ipg230103.xml']

MAX_ENTRIES = 1000

# utils_path = os.path.abspath('utils')
# sys.path.append(utils_path)

# load the psycopg to connect to postgresql
# from db_interface import PGDBInterface

def print_lines(text):
    """
    Prints line by line, with the line number
    """
    count = 1
    for line in text.split("\n"):    
        print(count, line)
        count += 1    

def parse_uspto_file(bs, logging=False):
    """
    Parses a USPTO patent in a BeautifulSoup object.
    """

    application_type = bs.find('application-reference')['appl-type']

    if application_type != 'utility':
        return None

    abstracts = []
    for el in bs.find_all('abstract'):
        abstracts.append(el.text.strip('\n'))
    
    # FILTERING OUT NO ABSTRACT PATENTS HERE
    if len(abstracts) == 0:
        return None

    publication_title = bs.find('invention-title').text
    publication_num = bs['file'].split("-")[0]
    publication_date = bs.find('publication-reference').find('date').text
    


    # International Patent Classification (IPC) Docs:
    # https://www.wipo.int/classifications/ipc/en/
    sections = {}
    section_classes = {}
    section_class_subclasses = {}
    section_class_subclass_groups = {}
    for classes in bs.find_all('classifications-ipcr'):
        for el in classes.find_all('classification-ipcr'):

            section = el.find('section').text
                        
            classification  = section
            classification += el.find('class').text
            classification += el.find('subclass').text
            
            group = el.find('main-group').text + "/"
            group += el.find('subgroup').text

            sections[section] = True
            section_classes[section+el.find('class').text] = True
            section_class_subclasses[classification] = True
            section_class_subclass_groups[classification+" "+group] = True
            
    authors = []
    for parties in bs.find_all('parties'):
        for applicants in parties.find_all('applicants'):
            for el in applicants.find_all('addressbook'):
                first_name = el.find('first-name').text
                last_name = el.find('last-name').text
                authors.append(first_name + " " + last_name)

    publication_date = datetime.strptime(publication_date, '%Y%m%d') 

    descriptions = []
    for el in bs.find_all('description'):
        descriptions.append(el.text.strip('\n'))
        
    claims = []
    for el in bs.find_all('claim'):
        claims.append(el.text.strip('\n'))

    uspto_patent = {
        "publication_title": publication_title,
        "publication_number": publication_num,
        "publication_date": '{:%B %d, %Y}'.format(publication_date),
        "application_type": application_type,
        "authors": authors, # list
        "sections": list(sections.keys()),
        "section_classes": list(section_classes.keys()),
        "section_class_subclasses": list(section_class_subclasses.keys()),
        "section_class_subclass_groups": list(section_class_subclass_groups.keys()),
        "abstract": abstracts, # list
        "descriptions": descriptions, # list
        "claims": claims # list
    }
    # print(uspto_patent)
        
    if logging:
        
        # print(bs.prettify())
        
        print("Filename:", filename)
        print("\n\n")
        print("\n--------------------------------------------------------\n")

        print("USPTO Invention Title:", publication_title)
        print("USPTO Publication Number:", publication_num)
        print("USPTO Publication Date:", publication_date)
        print("USPTO Application Type:", application_type)
            
        count = 1
        for classification in section-class_subclass_groups:
            print("USPTO Classification #"+str(count)+": " + classification)
            count += 1
        print("\n")
        
        count = 1
        for author in authors:
            print("Inventor #"+str(count)+": " + author)
            count += 1

        print("\n--------------------------------------------------------\n")

        print("Abstract:\n-----------------------------------------------")
        for abstract in abstracts:
            print(abstract)

        print("Description:\n-----------------------------------------------")
        for description in descriptions:
            print(description)

        print("Claims:\n-----------------------------------------------")
        for claim in claims:
            print(claim)

    # title = "Shower shield system for bathroom shower drain areaways"
    # if bs.find('invention-title').text == title:
    #     print(bs)
    #     exit()

    return uspto_patent


def gen_entry(filename,uspto_patent):

    uspto_db_entry = {
        #"filename":filename,
        "publication_title": uspto_patent['publication_title'],
        "patent_number": uspto_patent['publication_number'],
        "publication_date": uspto_patent['publication_date'],
        "application_type": uspto_patent['application_type'],
        # "authors": ','.join(uspto_patent['authors']),
        #"sections": ','.join(uspto_patent['sections']),
        #"section_classes": ','.join(uspto_patent['section_classes']),
        #"section_class_subclasses": ','.join(uspto_patent['section_class_subclasses']),
        #"section_class_subclass_groups": ','.join(uspto_patent['section_class_subclass_groups']),
        "abstract": '\n'.join(uspto_patent['abstract']),
        # "descriptions": '\n'.join(uspto_patent['descriptions']),
        #"claims": '\n'.join(uspto_patent['claims'])
    }

    return uspto_db_entry

def write_to_db(uspto_patent, db=None):    

    """
    pp = pprint.PrettyPrinter(indent=2)
    for key in uspto_patent:
        if type(uspto_patent[key]) == list:
            if key == "section_class_subclass_groups":
                print("\n--------------------------------")
                print(uspto_patent['publication_title'])
                print(uspto_patent['publication_number'])
                print(uspto_patent['publication_date'])
                print(uspto_patent['sections'])
                print(uspto_patent['section_classes'])
                print(uspto_patent['section_class_subclasses'])
                print(uspto_patent['section_class_subclass_groups'])
                print("--------------------------------")
    """

    # Will use for created_at & updated_at time
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
    # INSERTS INTO DB
    uspto_db_entry = [
        uspto_patent['publication_title'],
        uspto_patent['publication_number'],
        uspto_patent['publication_date'],
        uspto_patent['application_type'],
        ','.join(uspto_patent['authors']),
        ','.join(uspto_patent['sections']),
        ','.join(uspto_patent['section_classes']),
        ','.join(uspto_patent['section_class_subclasses']),
        ','.join(uspto_patent['section_class_subclass_groups']),
        '\n'.join(uspto_patent['abstract']),
        '\n'.join(uspto_patent['descriptions']),
        '\n'.join(uspto_patent['claims']),
        current_time,
        current_time
    ]

    # ON CONFLICT UPDATES TO DB
    uspto_db_entry += [
        uspto_patent['publication_title'],
        uspto_patent['publication_date'],
        uspto_patent['application_type'],
        ','.join(uspto_patent['authors']),
        ','.join(uspto_patent['sections']),
        ','.join(uspto_patent['section_classes']),
        ','.join(uspto_patent['section_class_subclasses']),
        ','.join(uspto_patent['section_class_subclass_groups']),
        '\n'.join(uspto_patent['abstract']),
        '\n'.join(uspto_patent['descriptions']),
        '\n'.join(uspto_patent['claims']),
        current_time
    ]

    db_cursor = None
    if db is not None:
        db_cursor = db.obtain_db_cursor()
    
    if db_cursor is not None:

        db_cursor.execute("INSERT INTO uspto_patents ("
                          + "publication_title, publication_number, "
                          + "publication_date, publication_type, " 
                          + "authors, sections, section_classes, " 
                          + "section_class_subclasses, "
                          + "section_class_subclass_groups, "
                          + "abstract, description, claims, "
                          + "created_at, updated_at"
                          + ") VALUES ("
                          + "%s, %s, %s, %s, %s, %s, %s, %s, "
                          + "%s, %s, %s, %s, %s, %s) "
                          + "ON CONFLICT(publication_number) "
                          + "DO UPDATE SET "
                          + "publication_title=%s, "
                          + "publication_date=%s, "
                          + "publication_type=%s, "
                          + "authors=%s, "
                          + "sections=%s, section_classes=%s, "
                          + "section_class_subclasses=%s, "
                          + "section_class_subclass_groups=%s, "
                          + "abstract=%s, description=%s, "
                          + "claims=%s, updated_at=%s", uspto_db_entry)

    return 
    

filenames = []
for filename in arg_filenames:
    # Load listed directories
    if os.path.isdir(filename):
        print("directory", filename)
        for dir_filename in os.listdir(filename):
            directory = filename
            if directory[-1] != "/":
                directory += "/"
            filenames.append(directory + dir_filename)                
                
    # Load listed files
    if ".xml" in filename:
        filenames.append(filename)

print("LOADING FILES TO PARSE\n----------------------------")
for filename in filenames:
    print(filename)


# db_config_file = "config/postgres.tsv"
# db = PGDBInterface(config_file=db_config_file)
# db.silent_logging = True
    
count = 1
success_count = 0
errors = []
patentEntries=[]
for filename in filenames:
    if ".xml" in filename:
        
        xml_text = html.unescape(open(filename, 'r').read())
        
        for patent in xml_text.split("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"):

            if patent is None or patent == "":
                continue
    
            bs = BeautifulSoup(patent,features="html.parser")

            if bs.find('sequence-cwu') is not None:
                continue # Skip DNA sequence documents

            application = bs.find('us-patent-grant')
            if application is None: # If no application, search for grant
                application = bs.find('us-patent-application')
            title = "None"
    
            try:
                title = application.find('invention-title').text
            except Exception as e:          
                print("Error", count, e)

            uspto_patent=None
            try:
                uspto_patent = parse_uspto_file(application)
                #write_to_db(uspto_patent, db=db)
                #print(uspto_patent)
                if uspto_patent != None:

                    entry = gen_entry(filename,uspto_patent)

                    #print(entry['abstract'])

                    if len(entry['abstract']) > 0:
                        patentEntries.append(entry)

                        success_count += 1

            except Exception as e:
                
                exception_tuple = (count, title, e)
                errors.append(exception_tuple)
                print(exception_tuple)
            
            if uspto_patent != None:
                if (success_count+len(errors)) % 50 == 0:
                    print(success_count, filename, title)
                    #db.commit_to_db()
            count += 1

            # print(success_count)
            if success_count == MAX_ENTRIES:
                break


print("\n\nErrors\n------------------------\n")
for e in errors:
    print(e)
    
print("Success Count:", success_count)
print("Error Count:", len(errors))

df = pd.DataFrame(patentEntries)
#print(df)

df = df.replace(',',' ')

df.to_csv('parsed_data.csv',index=False,sep=',')
#print(df.to_markdown())

# for index, row in df.iterrows():

#     f = open('parsed_data/'+row['publication_number'].replace('Patent Number: ','')+'.md', 'w')

#     for key in row.keys():

#         f.write('### '+key+'\n')
#         f.write(row[key])
#         f.write('\n')

#     f.close()
