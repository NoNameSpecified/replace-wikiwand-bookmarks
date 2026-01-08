"""
contact: https://github.com/NoNameSpecified
created & last_updated: 2026-01-08

Little script to get rid of wikiwand links in FIREFOX bookmarks...
    ... and replace them with real wikipedia links !

Usage:
    1. export your bookmarks ("backup" in the Manage Bookmarks)
    2. edit the json filenames below, run this script
    3. import the new bookmarks file into firefox !

Note:
    Wikiwand not only uses "normal" /en/articlename URLs, but also /simple/ etc.
    This script only deals with "normal" articles
"""

import json

# put your old file here
old_file_link = "your_old_bookmarks.json"
# this will be the new bookmarks file, your old one won't be changed
new_file_link = "new_bookmarks.json"


class BookmarksCleaner:
    def __init__(self, old_file_link):
        # load old bookmarks json
        with open(old_file_link, "r", encoding="utf-8") as old_file:
            self.data = json.load(old_file)

        # Wikiwand/Wikipedia formatting things
        # this is not really used currently, but could be
        self.lang_list = ["en", "de", "fr", "es", "it", "pt", "ru",
                    "ja", "zh", "ar", "pl", "nl", "sv", "tr", "ko"] # add your langauges !
        self.wiki_icon_path = "https://de.wikipedia.org/static/favicon/wikipedia.ico" # de, but change if you want
        self.wikiwand_title_suffix = "- Wikiwand"
        self.wikipedia_title_suffix = "– Wikipedia"

    # General purpose functions
    @staticmethod
    def get_new_link(link):
        parts = link.split("/")
        for index, part in enumerate(parts):
            # example: wikiwand.com/de/articles/[actual article name]
            if part == "articles": parts.pop(index) # remove !

        # example: i have a link that goes
        #  "https://www.wikiwand.com/de/articles/[name]#/Mordmerkmale - with the extra #+slash somehow.
        if parts[-2].endswith("#"): # i.e. it was #/ and the ...# was split wrongfully
            parts[-2] = parts[-2] + parts[-1]
            parts.pop(-1)

        # now we should be able to use it normally
        name = parts[-1]
        lang = parts[-2]

        # leave be in case it's not a standard /en/articlename url.
        # catch cases where URL contains section
        if len(lang) > 2:
            print(f"Error at link {link}: not a standard URL. Skipping.")
            return link
        """ other possibility:
        if self.lang not in lang_list: (do as above) -- remove staticmethod for this
        """
        # else change up
        return f"https://{lang}.wikipedia.org/wiki/{name}"

    def get_new_title(self, title):
        """ --> this doesn't work if you edited your title to be "article - wikiwand (funny article lol)"
        if title.endswith(self.wikiwand_title_suffix):
            title = title.removesuffix(self.wikiwand_title_suffix)
            title = f"{title} {self.wikipedia_title_suffix}"
        """

        parts = title.split(self.wikiwand_title_suffix)
        # gives us ["article", "(funny article lol)"]
        # admitted, this is a bit tricky if by some reason you happen to have a bookmark title with
        #  several "- Wikiwand" in your title... If so please consider reviewing this lol.
        title = f"{parts[0]}{self.wikipedia_title_suffix} {parts[1]}"
        return title

    # The actual cleaning function
    def clean_node(self, subdata):
        # .get() is safer than if ... in subdata["uri"], because it shouldn't throw KeyErrors
        if not "wikiwand.com" in subdata.get("uri", ""):
            # skip if not what we're looking for
            return
        # else: start cleaning
        subdata["uri"] = self.get_new_link(subdata["uri"])
        if any(icon_link_parts in subdata.get("iconUri", "") for icon_link_parts in ["-19431.kxcdn.", "/icons/"]):
            subdata["iconUri"] = self.wiki_icon_path
        if self.wikiwand_title_suffix in subdata.get("title", ""):
            subdata["title"] = self.get_new_title(subdata["title"])

    # Move through the whole bookmarks block recursively
    def moonwalk(self, node = None):
        # top level ? else work with given data
        if node is None:
            node = self.data

        # start cleaning this node before going deeper
        if "uri" in node: # there's other types of data than just uri's, but we want only that
            self.clean_node(node)

        for child in node.get("children", []):
            self.moonwalk(child)

# Start
mrproper = BookmarksCleaner(old_file_link)
# Works recursively
mrproper.moonwalk()

# writing into new file
with open(new_file_link, "w", encoding="utf-8") as new_file:
    # ensure_ascii=True would make our beautiful "–" turn into u2013...
    # no indent because it's just to be eaten by firefox
    json.dump(mrproper.data, new_file, ensure_ascii=False)

# inform & exit
print(f"Your new bookmarks is now stored in {new_file_link} !")
print("You can go to firefox bookmarks manager and import the new file now.\n")
# in case you don't call this from terminal
input("exit...")
