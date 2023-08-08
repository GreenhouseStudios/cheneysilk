import arcgis
import pprint
import asyncio
import logging
import re
import time
from arcgis.gis import GIS
from arcgis.apps.storymap import Text, Image, StoryMap

# logger = logging.getLogger('cheneysilk')
# logger.setLevel(logging.DEBUG)
# # create file handler which logs even debug messages
# fh = logging.FileHandler('C:/Users/Tom/Documents/ArcGIS/Projects/cheneysilk/spam.log')
# fh.setLevel(logging.DEBUG)
# logger.addHandler(fh)

def is_valid_code(code):
    pattern = r'^[a-zA-Z0-9]{32}$'
    return re.match(pattern, code) is not None

def extract_anchor_content(html):
    pattern = r'<a[^>]*>(.*?)<\/a>'
    return re.findall(pattern, html)

def extract_anchor_tags_and_content(html):
    pattern = r'<a[^>]*>.*?<\/a>'
    return re.findall(pattern, html)

def extract_code(link):
    pattern = r'[a-zA-Z0-9]{32}'
    match = re.search(pattern,link)
    if match:
        return match.group()
    return None

def storymapTitleFromObj(storymap):
    return storymap(extract_code(storymap))

class LinkUpdate:
    old_text = ''
    new_text = ''
    storymap = ''
    imgpath = ''
    ty = ''
    change_num = 0
    success = False
    
    def __init__(self,old,new,story,typ):
        self.old_text = old
        self.new_text = new
        self.storymap = story
        self.ty = typ

    def report(self):
        pprint.pprint(self.storymap.cover()['data']['title'])
        print("<--- " + self.ty + " --->")
        print("\n")
        print(self.old_text)
        print("<--- Changes to: --->")
        print(self.new_text)
#         if self.ty == "image":
#             print(self.old_text)
        print("\n")
        
    def execute(self):
#         if self.ty == "image":
#             print(self.old_text.path)
#             self.storymap.add(Image(path=self.old_text))
        
        if self.old_text != self.new_text:
            print("Executing change...")
            print(self.old_text)
            print(self.new_text)
            self.old_text = self.new_text
            time.sleep(10)
            print(self.old_text)
        

gis = GIS("pro")
storyIds = set()
storymapObjects = []
idMapping = []
changeCount = 0
change_list = []
# mode = "test"
mode = "prod"


async def copyStory(story):
    print("Start copy")
    return story.duplicate()
    await asyncio.sleep(10)
    print("End copy")
    return copy

#Recursively scans site for story id codes
def get_children(storyID):
    main = gis.content.get(storyID)
    if not main:
        return
    d = main.get_data()
    textNodes = [n['data']['text'] for n in d['nodes'].values() if 'data' in n and 'text' in n['data']]
#     pprint.pprint(textNodes)
    imgNodes = [n['data']['caption'] for n in d['nodes'].values() if 'data' in n and 'caption' in n['data']]
#     pprint.pprint(imgNodes)
    for node in d['nodes'].values():
        if 'data' in node:
            n = node['data']
#             pprint.pprint(n)
            if 'embedSrc' in n:
                id = n['embedSrc'][-32:]
                get_children(id)
        
    for node in d['resources'].values():
        if 'data' in node:
            n = node['data']
            if n and 'itemId' in n and 'provider' not in n and is_valid_code(n['itemId']): #if item is a story
#                 print(n)
                item = gis.content.get(n['itemId'])
#                 if item and 'title' in item:
#                     print("Story to copy: " + item['title'])
                id = n['itemId']
                storyIds.add(id)
                get_children(id)
            
def duplicateStory(id):
    contentManager = arcgis.gis.ContentManager(gis) 
    seed = gis.content.get(id)
    copy = contentManager.clone_items(items=[seed])
    print(copy)
#     print(copy.get_data())
            
            
def itemToStoryMap(i):
    return StoryMap(i)

def dictFirstKey(dict):
    return next(iter(dict.keys()))
          
    
def findMatchingCode(oldCode):
    for pair in idMapping:
        if pair[0] == oldCode:
            return pair[1]
    return None

def replaceLink(link):
    original = link
    link = link.replace("storymaps.arcgis.com/stories/","cheneysilk.org/#/")
    link = link.replace("storymaps.arcgis.com/collections/","cheneysilk.org/#/")
#     link = link.replace("storymaps.arcgis.com/stories/","greenhousestudios.github.io/cheneysilk/#/")
#     link = link.replace("storymaps.arcgis.com/collections/","greenhousestudios.github.io/cheneysilk/#/")
    code = extract_code(link)
#     print(code)
    global changeCount
    newCode = findMatchingCode(code)
    if newCode != None:
        link = link.replace(code,newCode)
    if link != original:
        link = link.replace('"',"'")
        changeCount += 1
    return link
    
def replaceCaptionLink(link):
    link = replaceLink(link)
#     link.replace('_blank','_self')
#     print(link)
    return link

def checkBrokenLink(link):
#     print(link)
    if link.find("href=''") >= 0:
        print("Broken link: " + link)

def register_update(newText, typ):
    print("<--- " + typ + " --->")
    print("<--- Changes to: --->")
    print(newText)
    print("\n")

def handleSidecar(sidecar,story):
    changes = 0
    for thing in sidecar.properties:
#                 print(type(thing))
#                 print(thing)
#         if type(thing) is str:
#             print(sidecar.get(thing))
        if type(thing) is dict:
            slide = sidecar.get(dictFirstKey(thing))
            for th in thing.values():
#                 print("children: " + str(th['narrative_panel']['children']))
                for thi in th['narrative_panel']['children'].values():
                    sup = sidecar.get(thi)
#                     print("type: " + str(type(sup)))
                    if hasattr(sup,'text'):
#                         print(sup.text)
                        temp = replaceLink(sup.text)
                        if temp != sup.text:
#                             print(sup.text)
#                             register_update(temp,"sidecar")
                            change_list.append(LinkUpdate(sup.text,temp,story,"sidecar"))
                            changes += 1
                    else:
                        try: 
                            if hasattr(sup,'caption'):
#                         print(sup.caption)
                                temp = replaceLink(sup.caption)
                                if temp != sup.caption:
#                                     print(sup.caption)
#                                     register_update(temp,"sidecar")
                                    change_list.append(LinkUpdate(sup.caption,temp,story,"sidecar"))
                                    changes += 1
                        except KeyError:
#                             print("No caption")
                            pass
                    
    return changes
                    
def scanStory(story):
    mode = "test"
    st = gis.content.get(story)
    textChanges = 0
    linkChanges = 0
    sidecarChanges = 0
    title = gis.content.get(story)
    s = st.get_data()
#     print(title) 
#         pprint.pprint(s)
    storymap = StoryMap(story)
#         print(storymap) #prints URL of the storymap

    #Get the different types of content from the storymap
    sidecars = storymap.get(type="sidecar")
    images =  storymap.get(type="image")
    textBlocks = storymap.get(type="text")
#         print(textBlocks)
#         pprint.pprint(paragraphs)
#         print(images)

    for sc in sidecars:
        sidecar = storymap.get(dictFirstKey(sc))
        sidecarChanges += handleSidecar(sidecar,storymap)

    for t in textBlocks:
        block = storymap.get(dictFirstKey(t))
#             print(block.text)
        newText = replaceLink(block.text)
        if block.text != newText:
#                 print(block.text)
            change_list.append(LinkUpdate(block.text,newText,storymap,"text"))
        block.text = newText

    for i in images:
#             print(i)
        oldImage = storymap.get(dictFirstKey(i))
        try:
#             print(oldImage.image)
#             print(oldImage.properties['node_dict'])
            newLink = replaceCaptionLink(oldImage.caption)
            checkBrokenLink(oldImage.caption)
#                 print(oldImage.caption)
            if oldImage.caption != newLink:
                change_list.append(LinkUpdate(oldImage.caption,newLink,storymap,"image"))

#                 oldImage.caption = newLink
        except KeyError:
            pass
    print("\n")
    
async def main():
    get_children("bf84e6ebd1c2456a9cdc721779043c01") #Cheney Silk Collection
# get_children("9ffd5cb43fb04125ab10a238a2361bb5") #Historical Narratives Collection
# get_children("c82fbf57c58d42dfb4e285aa4791b7b5") #Welfare Capitalism

    my_content = gis.content.search(query="owner:" + gis.users.me.username, 
                                item_type="StoryMap", 
                                max_items=55)
    
    oldIds = list(storyIds)
#     oldIds.append("d1491a66572948e1b2832894b8641238")
    
#     if "6ae7ca97886245a390367b3c41835ee9" not in oldIds:
#         oldIds.append("6ae7ca97886245a390367b3c41835ee9") #Frank Weir
# #     print(oldIds)

    matchedIds = []
    unmatched = set()
    for id in oldIds:
        s = gis.content.get(id)
#         print(s.title)
        for j in my_content: #scan list of my stories
            if s.title == j.title:
                idMapping.append([id,j.id])
                matchedIds.append(id)
                break
        if id not in matchedIds:
            unmatched.add(id)
    
# #     print(idMapping)

    print("Stories that need to be copied")
    for id in list(unmatched):
#         print(id)
        s= StoryMap(id)
        print(s.cover()['data']['title'])
#         duplicateStory(id)

# This block copies all the stories nested in the embed structure
#     contentManager = arcgis.gis.ContentManager(gis)    
#     l = list(storyIds)
#     for story in l:
#         if story not in matchedIds  
#             seed = gis.content.get(story)
#             copy = contentManager.clone_items(items=[seed])
#             print(copy)
#             print(copy.get_data())

#     print("Total Stories: " + str(len(list(my_content))))
#     count = 1
    
#List new stories
#     for story in my_content:
#         print(count)
#         s = gis.content.get(story.id)
#         print(s)
#         print(s.owner)
#         story = StoryMap(story.id)
#         print(story)
# #         pprint.pprint(s.properties)
#         count += 1
#         print("\n")
        
    newStories = []
    for story in my_content:
        newStories.append(story.id)
        
    newStories.sort()
    
#     n = 19
#     n = 3
    mode = "test"
    print("Script running in " + mode + " mode...")
    
#     for count, story in enumerate(newStories):
#         st = gis.content.get(story)
#         print(count)
#         print(st)
#         print("\n")
        
#     for story in newStories[n:n+1]:
    storyCount = 0
    for story in newStories:
        print("-###- Story #" + str(storyCount+1))
        scanStory(story)
        storyCount += 1
    
    storiesWithChanges = set()
    for change in change_list:
        storiesWithChanges.add(change.storymap)
    
    print("[--- Stories with Changes ---]")
    for s in list(storiesWithChanges):
        print(s.cover()['data']['title'])
    
    print("Total changes: " + str(changeCount))
    
    currentStory = None
    for count,change in enumerate(change_list):
        print("Change #"  + str(count+1))
        change.report()
        change.execute() 
        
    if mode == "prod":
        for story in list(storiesWithChanges):    
            print('Saving changes for: ')
            print(story.cover()['data']['title'])
            story.save()


asyncio.run(main())

# duplicateStory("9ffd5cb43fb04125ab10a238a2361bb5") #Historical Narratives
# duplicateStory("58b2f050962b4225af36d49a3b63c675") #Personal Stories
# duplicateStory("093cccb1aedf469ea464b281414d361b") #MiracleWorkers
# duplicateStory("32c6c63056f642b3b2ffc6455ed9757c") #About

# duplicateStory("8a861d2eb00845378f2ee66b4f0f1a77") #hb cheney
# duplicateStory("d1491a66572948e1b2832894b8641238")
# duplicateStory("9ff94f1482304f088d4f2f42882670cd") #Filomena
# duplicateStory("fea9dff24bd14cbc96526902b9cb9a6d") #FavorableWorkingConditions
# duplicateStory("f8fc28d94d014db6aa191de039cbc702") #HattieMarshall
# duplicateStory("c82fbf57c58d42dfb4e285aa4791b7b5") #welfareCapitalism
# duplicateStory("ea74f9c44f3d4ad6a102de96e07697d2") #EuroSilkMigration
# duplicateStory("e0dfacb377c3488dbaa4a5f47692ab26") #MillWorkersHomeLife
# duplicateStory("6ae7ca97886245a390367b3c41835ee9") #FrankWeir
# duplicateStory("264f5f7029fc4e5daa67c4f2554bd0a7") #FrankCheneyFoundingBrothers
# duplicateStory("289d4710db3748e5b09bc22f8d8eaebd") #Lifestyle Inequality
# duplicateStory("d1491a66572948e1b2832894b8641238") #Robert McDowell
# duplicateStory("fea9dff24bd14cbc96526902b9cb9a6d") #FavorableWorkingConditions

# duplicateStory("660a1cbd115d4681956ddc36924d8b34") #FWCheneyAndTheNextGeneration

#https://storymaps.arcgis.com/stories/c4ce7ea378af4a54aca877817f86c2f2#ref-n-eHgado
        