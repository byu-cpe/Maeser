import wikipediaapi

wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='Maeser AI Example',
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI
)

p_wiki = wiki_wiki.page("Karl G. Maeser")
text = p_wiki.text