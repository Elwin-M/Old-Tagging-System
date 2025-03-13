from main import pass_to_service

#make request
def make_request(session, url, method="GET", data=None):
    import requests
    if method == "GET":
        response = session.get(url)
    elif method == "POST":
        response = session.post(url, json=data)
    elif method == "DELETE":
        response = session.delete(url)
    response.raise_for_status()
    return response.json()


#get all seasonal/ old
def list_tag(session, instance, seasonal_tag, old_tag):
    url = f"{instance}/api/v3/tag"
    #print(f"{instance}/api/v3/tag")
    tags = pass_to_service(session, url)
    #print(tags)
    seasonal_items = [item for item in tags if seasonal_tag in item["tags"]]
    #old_items = [item for item in tags if old_tag in item["tags"]]
    print(seasonal_items)
    #return seasonal_items, old_items


#add OLDTAG (SEASONAL + OLDDAYSCOUNT)
def add_tag(session, instance, seasonal_tag, old_tag, old_days_count):
    items, _ = list_tag(session, instance, seasonal_tag, old_tag)
    for item in items:
        added_date = datetime.strptime(item["added"], "%Y-%m-%d")
        if (datetime.now() - added_date).days > old_days_count:
            item["tags"].append(old_tag)
            url = f"{instance}/api/v3/tag/{item['id']}"
            make_request(session, url, method="POST", data=item)


#remove delete tag if not in seasonal / redundant if used in arr instance
def remove_tag(session, instance):
    items, old_items = list_tag(session, instance, seasonal_tag, old_tag)
    for item in old_items:
        if seasonal_tag not in item["tags"]:
            item["tags"].remove(old_tag)
            url = f"{instance}/api/v3/tag/{item['id']}"
            make_request(session, url, method="POST", data=item)


#check if add date is past OLDDAYSCOUNT
def check_date(item, old_days_count):
    added_date = datetime.strptime(item["added"], "%Y-%m-%d")
    return (datetime.now() - added_date).days > old_days_count


#move to OLDDIR
def move_files(item, old_dir):
    file_path = item["path"]
    target_path = os.path.join(old_dir, os.path.basename(file_path))
    shutil.move(file_path, target_path)

#delete files past expiration in OLDDIR (HAS OLDTAG + PAST EXPIRATIONDAYSCOUNT)
def delete_files(old_dir, expiration_days_count):
    now = datetime.now()
    for root, _, files in os.walk(old_dir):
        for file in files:
            file_path = os.path.join(root, file)
            modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if (now - modified_time).days > expiration_days_count:
                os.remove(file_path)
