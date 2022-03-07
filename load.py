import sys
import tkinter as tk
import requests
import json
import os
import logging
from config import appname, appversion, config

inventory = dict()

# For compatibility with pre-5.0.0
if not hasattr(config, 'get_int'):
    config.get_int = config.getint

if not hasattr(config, 'get_str'):
    config.get_str = config.get

if not hasattr(config, 'get_bool'):
    config.get_bool = lambda key: bool(config.getint(key))

if not hasattr(config, 'get_list'):
    config.get_list = config.get

plugin_name = os.path.basename(os.path.dirname(__file__))

# Logger per found plugin, so the folder name is included in
# the logging format.
logger = logging.getLogger(f'{appname}.{plugin_name}')
if not logger.hasHandlers():
    level = logging.INFO  # So logger.info(...) is equivalent to print()

    logger.setLevel(level)
    logger_channel = logging.StreamHandler()
    logger_channel.setLevel(level)
    logger_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')  # noqa: E501
    logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
    logger_formatter.default_msec_format = '%s.%03d'
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)


def plugin_start3(plugin_dir):
    logger.info( "Mission Status started")
    return "Mission Status"

def plugin_stop():
	"""
	EDMC is closing
	"""
	logger.info( "Mission start unloaded!" )

def journal_entry(cmdr, is_beta, system, station, entry, state):
    logger.info( "EVENT: %s ",entry['event'])
    is_mission_related = False
    if entry['event'] == 'MissionAccepted':
        is_mission_related = True
        # { "timestamp":"2022-03-06T16:37:47Z", 
        #   "event":"MissionAccepted", 
        #   "Faction":"Perez Ring Brewery", 
        #   "Name":"Mission_PassengerBulk", 
        #   "LocalisedName":"12 Tourists Seeking Transport", 
        #   "DestinationSystem":"Phekda", 
        #   "DestinationStation":"Leckie Town", 
        #   "Expiry":"2022-03-06T19:13:12Z", 
        #   "Wing":false, 
        #   "Influence":"++", 
        #   "Reputation":"++", 
        #   "Reward":381616, 
        #   "PassengerCount":12, 
        #   "PassengerVIPs":false, 
        #   "PassengerWanted":false, 
        #   "PassengerType":"Tourist", 
        #   "MissionID":852166136 
        #   }
        if (entry["MissionID"] not in inventory):
            inventory[entry["MissionID"]] = entry
        logger.info( "%s | %s",entry['event'],entry)

    elif entry['event'] == 'MissionUpdated':
        is_mission_related = True
        inventory[entry["MissionID"]] = entry
        logger.info( "%s | %s",entry['event'],entry)

    elif entry['event'] == 'MissionCompleted':
        is_mission_related = True
        remove_key = inventory.pop(entry["MissionID"], None)
        # { "timestamp":"2021-06-08T17:25:38Z",
		#  "event":"MissionCompleted",
		#  "Faction":"Omicron Columbae Patrons of Law",
		#  "Name":"Mission_Delivery_    RankEmp_name",
		#  "MissionID":780617802,
		#  "Commodity":"$NonLethalWeapons_Name;",
		#  "Commodity_Localised":"Non-Lethal Weapons",
		#  "Count":180,
		#  "DestinationSystem":"Uenne",
		#  "    DestinationStation":"Gorbatko Port",
		#  "Reward":2705104,
		#  "FactionEffects":
        #       [ 
        #           { "Faction":"Uenne Gold Netcoms Holdings",
		#               "Effects":[  ],
		#  "Influence":[  ],
		#  "ReputationTr    end":"UpGood",
		#  "Reputation":"++" },
		#  { "Faction":"Omicron Columbae Patrons of Law",
		#  "Effects":[ { "Effect":"$MISSIONUTIL_Interaction_Summary_EP_up;",
		#  "Effect_Localis    ed":"The economic status of $#MinorFaction; has improved in the $#System; system.",
		#  "Trend":"UpGood" } ],
		#  "Influence":[ { "SystemAddress":908620436170,
		#  "Trend":"UpG    ood",
		#  "Influence":"+++" } ],
		#  "ReputationTrend":"UpGood",
		#  "Reputation":"++" } ] }
        logger.info( "%s | %s",entry['event'],entry)

    elif entry['event'] == 'MissionRedirected':
        is_mission_related = True
        inventory[entry["MissionID"]] = entry
        # { "timestamp":"2021-06-13T18:26:51Z",
		#  "event":"MissionRedirected",
		#  "MissionID":782742974,
		#  "Name":"Mission_PassengerBulk",
		#  "NewDestinatio    nStation":"Lee Depot",
		#  "NewDestinationSystem":"Arjung",
		#  "OldDestinationStation":"Petaja Holdings",
		#  "OldDestinationSystem":"Gitxsanluga" }
        logger.info( "%s | %s",entry['event'],entry)
    elif entry['event'] == 'Missions':
        is_mission_related = True
        #{ "timestamp":"2021-06-13T17:54:12Z",
		#  "event":"Missions",
		#  "Active":[ { "MissionID":782711699,
		#  "Name":"Mission_OnFoot_Collect_008_name",
		#      "PassengerMission":false,
		#  "Expires":19034 } ],
		#  "Failed":[  ],
		#  "Complete":[  ] }
        logger.info( "%s | %s",entry['event'],entry)
        
    elif entry['event'] == 'MissionAbandoned':
        is_mission_related = True
        remove_key = inventory.pop(entry["MissionID"], None)
        # { "timestamp":"2021-06-13T17:54:31Z",
		#  "event":"MissionAbandoned",
		#  "Name":"Mission_OnFoot_Collect_008_name",
		#  "MissionID":782711699 }
        logger.info( "%s | %s",entry['event'],entry)
    
    if is_mission_related:
        logger.info("Inventory: %s",json.dumps(inventory, indent=4, sort_keys=True))
        

def cmdr_data(data, is_beta):
	pass