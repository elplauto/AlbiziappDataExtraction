# Before running this program
# Copy datas from https://albiziapp.reveries-project.fr/api/history
# Paste datas in the file extractionTraces/input/traces.json

# You can use https://jsonformatter.curiousconcept.com/ to format the JSON correctly
# However this website won't work if there is too much data in the JSON

import json
import csv
import os
import glob
import re
import argparse
import datetime

def start_activity(trace, activities):

    ongoing_activity_index = -1

    for cpt, activity in enumerate(trace['object']):
        if activity['statut'] == 'onGoing':
            ongoing_activity_index = cpt

        activities[cpt][1] = activity['statut']

    if ongoing_activity_index != -1:
        activities[ongoing_activity_index][2] = trace['date']


def end_activity(trace, activities):
    done_activity_index = -1

    for cpt, activity in enumerate(trace['object']):
        if activity['statut'] == 'done' or activity['statut'] == 'skipped' :
            done_activity_index = cpt

        activities[cpt][1] = activity['statut']

    if done_activity_index != -1:
        activities[done_activity_index][3] = trace['date']


def new_observation (trace, releves):

    if 'activity' in trace.keys():

        releve = [None for i in range(10)]

        index = trace['activity']['index']

        releve[0] = 'INVENTORY'

        extract_releve_data(releve,trace)

        releves[index].append(releve)


def verify_observation(trace, releves):

    releve = [None for i in range(10)]
    index = trace['activity']['index']
    releve[0] = 'VERIFY'
    extract_releve_data(releve,trace)
    releves[index].append(releve)

def identification(trace, releves):

    releve = releve = [None for i in range(13)]
    index = trace['activity']['index']
    releve[0] = 'IDENTIFY'

    if 'common' in trace['object']['identificationValue']:
        releve[1] = trace['object']['identificationValue']['common']

    if 'specie' in trace['object']['identificationValue']:
        releve[2] = trace['object']['identificationValue']['specie']

    if 'genus' in trace['object']['identificationValue']:
        releve[3] = trace['object']['identificationValue']['genus']

    releve[4] = 'oui' if 'image' in trace['object']['identificationValue'] else 'non'
    releve[5] = trace['object']['location']['coordinates'][0]
    releve[6] = trace['object']['location']['coordinates'][1]

    releve[7] = 'N/A'
    releve[8] = 'N/A'
    releve[9] = 'N/A'

    if 'common' in trace['object']:
        releve[10] = trace['object']['common']

    if 'specie' in trace['object']:
        releve[11] = trace['object']['specie']

    if 'genus' in trace['object']:
        releve[12] = trace['object']['genus']

    releves[index].append(releve)

def new_status(trace, status):

    index = trace['activity']['index']

    for each in trace['object']:
        status_name = each['name']

        for statut in status:
            if statut[0] == "Statut " + status_name:
                if statut[1] == "Non obtenu":
                    statut[1] = "Activité " + str(index)


def update_score(trace, activities):

    index = trace['activity']['index']

    for score in trace['object']:


        if score['name'] == 'knowledgePoints':       
            
            for i in range(index, len(activities)):    
                activities[i][4] = score['nbPoint']

        if score['name'] == 'explorationPoints':  

            for i in range(index, len(activities)):    
                activities[i][5] = score['nbPoint']


def new_trophy(trace, trophies):
    count = 0

    for each in trace['object']:
        trophyName = each['name']
        obtenu = each['obtenu']
        trophies[count][0] = 'Trophée ' + trophyName
        trophies[count][1] = 'Obtenu' if obtenu else 'Non obtenu'
        count += 1

def extract_releve_data(releve, trace):

    if 'common' in trace['object']:
        releve[1] = trace['object']['common']

    if 'specie' in trace['object']:
        releve[2] = trace['object']['specie']

    if 'genus' in trace['object']:
        releve[3] = trace['object']['genus']

    releve[4] = 'oui' if 'image' in trace['object'] else 'non'
    releve[5] = trace['object']['location']['coordinates'][0]    
    releve[6] = trace['object']['location']['coordinates'][1]

    if 'confidence' in trace['object']:
        releve[7] = trace['object']['confidence']

    releve[8] = 'oui' if trace['event'] == 'questionTree' else 'non'
    releve[9] = 'oui' if trace['event'] == 'validateObservation' else 'non'


def score_by_activity(activities):

    for i in range(1, len(activities)):
        index = len(activities)-i
        activities[index][4] -= activities[index-1][4]
        activities[index][5] -= activities[index-1][5]


def func_to_execute(trace, activities, releves, trophies, status, file_id):
    if 'userId' in trace.keys() and trace['userId'] == file_id:

        if trace['event'] == 'startActivity':
            start_activity(trace, activities)

        elif trace['event'] == 'endActivity':
            end_activity(trace, activities)

        elif trace['event'] == 'newObservation':
            new_observation(trace, releves)

        elif trace['event'] == 'validateObservation':
            verify_observation(trace, releves)

        elif trace['event'] == 'modifyObservation':
            verify_observation(trace, releves)

        elif trace['event'] == 'identification':
            identification(trace, releves)

        elif trace['event'] == 'newTrophy':  
            new_trophy(trace, trophies)

        elif trace['event'] == 'newStatus': 
            new_status(trace, status)

        elif trace['event'] == 'updateScore': 
            update_score(trace, activities)

        elif trace['event'] == 'questionTree':    
            verify_observation(trace, releves)

def parse_args():
    """ Arguments parser. """

    parser = argparse.ArgumentParser()
    parser.add_argument("year1", type=int, help="Year of the first date format YYYY")
    parser.add_argument("month1", type=int, help="Month of the first date format MM")
    parser.add_argument("day1", type=int, help="Day of the first date format DD")
    parser.add_argument("hour1", type=int, help="Hour of the first date format HH")
    parser.add_argument("minute1", type=int, help="Minute of the first date format MM")
    parser.add_argument("second1", type=int, help="Second of the first date format SS")
    
    parser.add_argument("year2", type=int, help="Year of the second date format YYYY")
    parser.add_argument("month2", type=int, help="Month of the second date format MM")
    parser.add_argument("day2", type=int, help="Day of the second date format DD")
    parser.add_argument("hour2", type=int, help="Hour of the second date format HH")
    parser.add_argument("minute2", type=int, help="Minute of the second date format MM")
    parser.add_argument("second2", type=int, help="Second of the second date format SS")

    args = parser.parse_args()

    return args


def main(args):

    from datetime import datetime

    datetime1 = datetime(args.year1, args.month1, args.day1, args.hour1, args.minute1, args.second1, 0)
    datetime2 = datetime(args.year2, args.month2, args.day2, args.hour2, args.minute2, args.second2, 0)

    if datetime1 > datetime2:
        print("La première date doit être inférieure à la deuxième")
        sys.exit()

    print("Traces analysées du " + datetime1.strftime("%d/%m/%Y, %H:%M:%S") + " au " + datetime2.strftime("%d/%m/%Y, %H:%M:%S"))

    # open a file for reading
    infile = open('../input/traces.json', 'r')

    # data model
    ligne_act = ["Activité",
                 "Statut",
                 "Date début",
                 "Date fin",
                 "Points de connaissance",
                 "Points d'exploration"]

    ligne_releve = ["Type",
                    "Nom commun",
                    "Espece",
                    "Genre",
                    "Photo",
                    "Longitude",
                    "Latitude",
                    "Taux de confiance",
                    "Mettre en doute",
                    "Confirmation"]

    releve_act_4 = ["Nom commun expert",
                    "Espece expert",
                    "Genre expert"]


    with open('../input/traces.json', 'r', encoding='utf8') as infile:
        unique_id_list = []                  
        #add each unique id in unique_id_list
        traces = [a for a in json.loads(infile.read())]
        for trace in traces:  
            date_object = datetime.strptime(trace['date'], "%Y-%m-%dT%H:%M:%S.%fZ")

            if date_object > datetime1 and date_object < datetime2:     
                if 'userId' in trace.keys() and trace['userId'] not in unique_id_list:
                    unique_id_list.append(trace['userId'])

    for file_id in unique_id_list:

        # Better to open it this way (auto-close at the end)
        with open("../output/csv/" + file_id + '.csv', 'w', newline='') as outfile:

            activities = [
                [1,"","","",0,0],
                [2,"","","",0,0],
                [3,"","","",0,0],
                [4,"","","",0,0],
                [5,"","","",0,0]
            ]

            releves = [
                [],[],[],[],[]
            ]

            trophies = [
                ["Trophée 1","Non obtenu"],
                ["Trophée 2","Non obtenu"],
                ["Trophée 3","Non obtenu"],
                ["Trophée 4","Non obtenu"],
                ["Trophée 5","Non obtenu"]
            ]

            status = [
                ["Statut Voyageur","Non obtenu"],
                ["Statut Voyageur confirmé","Non obtenu"],
                ["Statut Voyageur expérimenté","Non obtenu"],
                ["Statut Curieux des bois","Non obtenu"],
                ["Statut Explorateur de la forêt","Non obtenu"],
                ["Statut Routard des étendues forestières","Non obtenu"],
                ["Statut Observateur attenboisé","Non obtenu"],
                ["Statut Explorateur-botaniste aguerri","Non obtenu"],
                ["Statut Maître explorateur botaniste","Non obtenu"],
                ["Statut Oeil d'aigle des arbres","Non obtenu"],
                ["Statut Archéologue botaniste","Non obtenu"],
                ["Statut Grand maître arbalétiste","Non obtenu"]
            ]

            # We open the json file here, since it's only needed here
            with open('../input/traces.json', 'r', encoding='utf8') as infile:
                traces = [a for a in json.loads(infile.read())]
                for trace in traces:  
                    date_object = datetime.strptime(trace['date'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    # All the if elif statement is put inside a function (for readability purpose)
                    func_to_execute(trace, activities, releves, trophies, status, file_id)
            # The file is automatically closed here

            score_by_activity(activities)

            # create the csv writer object
            csvwriter = csv.writer(outfile)

            for cpt, activity in enumerate(activities):   

                csvwriter.writerow(ligne_act)
                csvwriter.writerow(activity)

                if cpt == 3:
                    csvwriter.writerow(ligne_releve + releve_act_4)

                else:
                    csvwriter.writerow(ligne_releve)

                csvwriter.writerows(releves[cpt])

            csvwriter.writerow(["Mécaniques de jeu", "Etat"])

            csvwriter.writerows(trophies)
            csvwriter.writerows(status)

    #put all the csv files created with extraction.py into a single xlsx file
    from xlsxwriter.workbook import Workbook

    workbook = Workbook('../output/xlsx/data.xlsx')

    for csvfile in glob.glob(os.path.join('../output/csv', '*.csv')):
        final_name = re.sub('[^0-9]', '', csvfile)
        worksheet = workbook.add_worksheet(final_name)

        with open(csvfile, 'rt', encoding='latin-1') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)

    workbook.close()

if __name__ == '__main__':
    args = parse_args()

    main(args)