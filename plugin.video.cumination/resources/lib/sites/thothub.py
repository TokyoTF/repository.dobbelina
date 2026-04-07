'''
    Cumination
    Copyright (C) 2026 Team Cumination

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
import time
from urllib import parse as urllib_parse
from resources.lib import utils
from resources.lib.decrypters.kvsplayer import kvs_decode
from resources.lib.adultsite import AdultSite


user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36'
site = AdultSite('thothub', '[COLOR hotpink]Thothub[/COLOR]', 'https://www.thothub.tube/', 'https://www.thothub.tube/static/images/logo1colo2r.png', 'thothub')
page = 2

# ListSites
# https://thothub.tube
# https://thothub.to
# https://thothub.lol
# https://thothub.mx

# ⚠ Spam warning: excessive requests may trigger anti-leech system and temporarily block your IP

BLOCKS = {
    'most-popular': ('list_videos_common_videos_list','video_viewed'),
    'latest-updates': ('list_videos_latest_videos_list','post_date'),
    'models': ('list_models_models_list','avg_videos_rating'),
    'search': ('list_videos_videos_list_search_result', ''),
    'none': ('list_videos_most_recent_videos','post_date')
}

@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Search[/COLOR]', site.url + 'search/', 'Search', site.img_search)
    site.add_dir('[COLOR hotpink]Latest Updates[/COLOR]', site.url + 'latest-updates/', 'List', site.img_next)
    site.add_dir('[COLOR hotpink]Most Popular[/COLOR]', site.url + 'most-popular/', 'List', site.img_next)
    site.add_dir('[COLOR hotpink]Categories[/COLOR]', site.url + 'categories/', 'Categories', site.img_cat)
    site.add_dir('[COLOR hotpink]Models[/COLOR]', site.url + 'models/', 'Models', site.img_cat)
    
    List(site.url)
    utils.eod()


@site.register()
def List(url):
    html = utils.getHtml(url, site.url)
    
    delimiter = 'class="item'
    re_videopage = 'href="([^"]+/videos/\d+/[^"]+/)"'
    re_name = 'title="([^"]+)"'
    re_img = 'data-original="([^"]+)"'
    re_duration = 'class="views-counter2"[^>]*>([^<]+)'

    for video in re.split(delimiter, html)[1:]:
        match = re.search(re_videopage, video)
        if not match:
            continue
        videopage = utils.fix_url(match.group(1), site.url)

        match = re.search(re_name, video)
        name = utils.cleantext(match.group(1)) if match else ''

        match = re.search(re_img, video)
        img = utils.fix_url(match.group(1).replace('&amp;', '&'), site.url) + '|User-Agent=' + user_agent + '|Referer=' + site.url if match else ''

        match = re.search(re_duration, video)
        duration = match.group(1) if match else ''

        site.add_download_link(name, videopage, 'thothub.Playvid', img, name, duration=duration)

    match = re.search(r'/(latest-updates|most-popular|models|search)/', url)
    nextp = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>Next</a>', re.DOTALL).search(html)

    if not nextp:
        return

    match_from_videos = re.search(r'&from_videos=(\d+)', url)
    match_from = re.search(r'&from=(\d+)', url)
    if match_from_videos:
        page = int(match_from_videos.group(1)) + 1
        next_url = re.sub(r'&from_videos=\d+', '&from_videos={0}'.format(page), url)
        next_url = re.sub(r'&from_albums=\d+', '&from_albums={0}'.format(page), next_url)
    elif match_from:
        page = int(match_from.group(1)) + 1
        next_url = re.sub(r'&from=\d+', '&from={0}'.format(page), url)
    elif match:
        page = 2
        section = match.group(1)
        block_id = BLOCKS[section][0]
        if match.group(1) == 'search':
            next_url = re.sub(r'\?.*', '', url) + '?mode=async&function=get_block&block_id={0}&q=&sort_by=&from_videos={1}&from_albums={2}&_={3}'.format(block_id, page, page, int(time.time() * 1000))
        else:
            next_url = nextp.group(1) + '?mode=async&function=get_block&block_id={0}&sort_by={1}&from={2}&_={3}'.format(block_id, BLOCKS[section][1], page, int(time.time() * 1000))
    else:
        page = 2
        next_url = site.url + '/?mode=async&function=get_block&block_id={0}&sort_by={1}&from={2}&_={3}'.format(BLOCKS['none'][0], BLOCKS['none'][1], page, int(time.time() * 1000))

    if match or match_from_videos or match_from:
        site.add_dir('Next Page >>', next_url, 'List', site.img_next)

    utils.eod()


@site.register()
def Categories(url):
    html = utils.getHtml(url, site.url)

    match = re.compile(r'<a class="item" href="([^"]+/categories/[^"]+/)" title="([^"]+)">', re.DOTALL).findall(html)
    for catpage, name in match:
        site.add_dir(name, catpage, 'List', site.img_cat, '')
    utils.eod()


@site.register()
def Models(url):
    html = utils.getHtml(url, site.url)
 
    delimiter = 'class="item'
    re_modelpage = 'href="([^"]+/models/[^"]+/)"'
    re_name = 'title="([^"]+)"'
    re_img = 'class="thumb" src="([^"]+)"'

    modellist = re.split(delimiter, html)
    if modellist:
        modellist.pop(0)
        for model in modellist:
            match_url = re.search(re_modelpage, model, flags=re.DOTALL | re.IGNORECASE)
            match_name = re.search(re_name, model, flags=re.DOTALL | re.IGNORECASE)
            match_img = re.search(re_img, model, flags=re.DOTALL | re.IGNORECASE)
            
            if match_url and match_name:
                img = match_img.group(1) if match_img else site.img_cat
                if img != site.img_cat:
                    re_img_format = "{0}|{1}".format(re_img, {'Referer': site.url})
                    img = re_img_format
                site.add_dir(match_name.group(1), match_url.group(1), 'List', img, '')

    if 'from=' in url:
        match = re.search(r'from=(\d+)', url)
        page = int(match.group(1)) + 1 if match else 2
        next_url = re.sub(r'from=\d+', 'from={}'.format(page), url)
        next_url = re.sub(r'&_=\d+', '&_={}'.format(int(time.time() * 1000)), next_url)
        site.add_dir('Next Page >>', next_url, 'Models', site.img_next)
    else:
        nextp = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>Next</a>', re.DOTALL).search(html)
        if nextp:
            site.add_dir('Next Page >>', site.url + nextp.group(1), 'Models', site.img_next)

    utils.eod()


@site.register()
def Search(url, keyword=None):
    if not keyword:
        site.search_dir(url, 'Search')
    else:
        search_term = urllib_parse.quote_plus(keyword)
        search_url = site.url + 'search/{0}/'.format(search_term)
        List(search_url)


@site.register()
def Playvid(url, name, download=None):

    vp = utils.VideoPlayer(name, download)
    html = utils.getHtml(url)
    
    license = re.search(r"license_code:\s*'(\$\d+)",html, flags=re.DOTALL | re.IGNORECASE)
    video_url = re.search(r"video_url:\s*'([^']+)",html, flags=re.DOTALL | re.IGNORECASE)
    
    if license and video_url:
        lc = license.group(1)
        vu = video_url.group(1)
        
        final_url = kvs_decode(vu, lc)

        final_url += '|User-Agent={0}&Referer={1}'.format(user_agent, url)
        vp.play_from_direct_link(final_url)
    else:
        vp.play_from_site_link(url + ('/' if not url.endswith('/') else ''))
