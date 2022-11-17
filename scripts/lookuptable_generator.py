# This tool generates the lookup tables we need to display additional informations.
# YOU DONT HAVE TO RUN THIS FILE YOURSELF! THE RESULTING DATA IS SHIPPED WITH THE MOD ALREADY!

import xml.etree.ElementTree as ET

filePath = "D:\\Programme\\Steam\\steamapps\\common\\The Binding of Isaac Rebirth\\resources-dlc3\\"
# filePath = "D:\\Program Files\\Steam\\steamapps\\common\\The Binding of Isaac Rebirth\\resources-dlc3\\"

# take second element for sort
def sortByID(elem):
    return elem["id"]
recipes = []
itempools = {}
itemIDToPool = {}
maxItemID = 0
cardMetadatas = []
pillMetadatas = []
entityNames = []

recipeIngredients = {}
#Poop, Penny
recipeIngredients["_"] = 29
recipeIngredients["."] = 8
#Red, Soul, Black Heart
recipeIngredients["h"] = 1
recipeIngredients["s"] = 2
recipeIngredients["b"] = 3
#Key, Bomb, Card
recipeIngredients["/"] = 12
recipeIngredients["v"] = 15
recipeIngredients["["] = 21
#Gold Heart, Eternal Heart, Pill
recipeIngredients["g"] = 5
recipeIngredients["e"] = 4
recipeIngredients["("] = 22
#Rotten Heart, Gold Key, Giga Bomb
recipeIngredients["r"] = 7
recipeIngredients["|"] = 13
recipeIngredients["V"] = 17
#Gold Bomb, Bone Heart
recipeIngredients["^"] = 16
recipeIngredients["B"] = 6
#Dice Shard, Cracked Key
recipeIngredients["?"] = 24
recipeIngredients["~"] = 25

# Read recipes.xml
recipesXML = ET.parse(filePath+'recipes.xml').getroot()
for recipe in recipesXML.findall('recipe'):
    input = recipe.get('input')
    convertedInput = []
    for char in input:
        convertedInput.append(recipeIngredients[char])

    convertedInput.sort()
    convertedInput = str(convertedInput).replace(" ","").replace("[","").replace("]","")
    recipes.append({"input": convertedInput, "output": recipe.get('output')})

# Read items_metadata.xml
items_metadataXML = ET.parse(filePath+'items_metadata.xml').getroot()
for item in items_metadataXML.findall('item'):
    id = int(item.get('id'))
    if maxItemID < id:
        maxItemID = id
    itemIDToPool[id] = []

# Read itempools.xml
itempoolsXML = ET.parse(filePath+'itempools.xml').getroot()
currentpool = 0
for pool in itempoolsXML.findall('Pool'):
    items = []
    for item in pool.findall('Item'):
        id = int(item.get('Id'))
        items.append([id,float(item.get('Weight'))])
        itemIDToPool[id].append(currentpool)
    itempools[pool.get("Name")] = items
    currentpool += 1

# Read pocketitems.xml
pocketitemsXML = ET.parse(filePath+'pocketitems.xml').getroot()

for card in pocketitemsXML.findall('card'):
    cardMetadatas.append({ "id": card.get('id'), "mimiccharge": card.get('mimiccharge', 0)})

for rune in pocketitemsXML.findall('rune'):
    cardMetadatas.append({ "id": rune.get('id'), "mimiccharge": rune.get('mimiccharge', 0)})
cardMetadatas.sort(key=sortByID)

for pilleffect in pocketitemsXML.findall('pilleffect'):
    pillMetadatas.append({ "id": pilleffect.get('id'), "mimiccharge": pilleffect.get('mimiccharge', 0), "class":pilleffect.get('class')})
pillMetadatas.sort(key=sortByID)

# Read entities2.xml
entitiesXML = ET.parse(filePath+'entities2.xml').getroot()

for entity in entitiesXML.findall('entity'):
    theID = entity.get('id')
    theName = entity.get('name')
    if entity.get('variant'):
        theID += "." + entity.get('variant')
    if entity.get('subtype') and entity.get('subtype') != "0":
        theID += "." + entity.get('subtype')
    if theName[0] == '#':
        theName = theName[1:].replace('_',' ').title()
    entityNames.append({ "id": theID, "name": theName })

#Write xml file

newfile = open("eid_xmldata.lua", "w")
newfile.write("--This file was autogenerated using 'lookuptable_generator.py' found in the scripts folder\n")
newfile.write("--It will have to be updated whenever the game's item XML files are updated\n")


newfile.write("--The highest item ID found in this specific export of XML data\n")
newfile.write("--Crafting doesn't use the in-game enum, because otherwise array index out-of-bounds errors could occur immediately after a game update\n")
newfile.write("EID.XMLMaxItemID = "+str(maxItemID) + "\n")


newfile.write("--The fixed recipes, for use in Bag of Crafting\n")
newfile.write("EID.XMLRecipes = {")
for recipe in recipes:
    newfile.write("[\""+recipe["input"]+"\"] = "+str(recipe["output"])+", ")
newfile.write("}\n\n")


newfile.write("--The contents of each item pool, and the item's weight, for use in Bag of Crafting\n")
newfile.write("EID.XMLItemPools = {")
for poolName, data in itempools.items():
    newfile.write(""+str(data).replace("[","{").replace("]","}")+", -- "+poolName+"\n")
newfile.write("}\n\n")


newfile.write("--The pools that each item is in, for roughly checking if a given item is unlocked\n")
newfile.write("EID.XMLItemIsInPools = {")
for itemid, data in itemIDToPool.items():
    newfile.write("["+str(itemid)+"] = "+str(data).replace("[","{").replace("]","}")+", ")
newfile.write("}\n\n")


newfile.write("--Metadata found in Pocketitems.xml\n")
newfile.write("EID.cardMetadata = {")
for card in cardMetadatas:
    newfile.write("["+card["id"]+"] = {mimiccharge="+str(card["mimiccharge"])+"}, ")
newfile.write("}\n\n")

newfile.write("EID.pillMetadata = {")
for pill in pillMetadatas:
    newfile.write("["+pill['id']+"] = {mimiccharge="+str(pill['mimiccharge'])+", class=\""+str(pill['class'])+"\"}, ")

newfile.write("}\n\n")


newfile.write("--The name of each entity, for use in glitched item descriptions\n")
newfile.write("EID.XMLEntityNames = {")
tempString = ""
counter = 0
for entity in entityNames:
    counter = counter+1
    tempString += "[\""+entity['id']+"\"] = \""+entity['name']+"\", "
    if counter > 100:
        newfile.write(tempString+"\n")
        tempString =""
        counter = 0

newfile.write("}\n\n")

newfile.close()
print("SUCCESS")

