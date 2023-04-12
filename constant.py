HEADERS = {
    "X-Restli-Protocol-Version": "2.0.0",
    "X-Li-Pem-Metadata": "Voyager - Search Typeahead Page=global-search-typeahead-result",
    "Accept": "application/vnd.linkedin.normalized+json+2.1",
    "Csrf-Token": "",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
    "Referer": "https://www.linkedin.com/feed/",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Dest": "empty",
    "Host": "www.linkedin.com",
    "Accept-Encoding": "gzip, deflate",
    "Sec-Fetch-Mode": "cors",
    "X-Li-Lang": "en_US",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Sec-Ch-Ua-Mobile": "?0",
}

CONTACT_HEADERS = {
    "X-Restli-Protocol-Version": "2.0.0",
    "Accept": "application/vnd.linkedin.normalized+json+2.1",
    "Csrf-Token": "ajax:3890344252407511716",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
    "X-Li-Deco-Include-Micro-Schema": "true",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Dest": "empty",
    "Host": "www.linkedin.com",
    "Accept-Encoding": "gzip, deflate",
    "Sec-Fetch-Mode": "cors",
    "X-Li-Lang": "en_US",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Sec-Ch-Ua-Mobile": "?0",
}

X_Li_Track = '{"clientVersion":"1.12.2593","mpVersion":"1.12.2593","osName":"web","deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":1,"displayWidth":1680,"displayHeight":1050}'

SEARCH_ENDPOINT = 'https://www.linkedin.com:443/voyager/api/graphql?' + 'includeWebMetadata=true&variables=(start:{},origin:SWITCH_SEARCH_VERTICAL,query:(keywords:{},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.0814efb14ee283f3e918ff9608d705fd'
CONTACTS_ENDPOINT = 'https://www.linkedin.com/voyager/api/graphql?variables=(memberIdentity:{})&&queryId=voyagerIdentityDashProfiles.84cab0be7183be5d0b8e79cd7d5ffb7b'
PROFILE_ENDPOINT = 'https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{})&&queryId=voyagerIdentityDashProfileCards.b3af3663609a423adeca8d1019a6f19b'
PROFILE_ENDPOINT_2 = 'https://www.linkedin.com:443/voyager/api/graphql?includeWebMetadata=true&variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{},sectionType:skills,locale:en_US)&&queryId=voyagerIdentityDashProfileComponents.1a6f6d936902bb480940179c442456b2'