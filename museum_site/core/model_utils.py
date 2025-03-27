import os

from bs4 import BeautifulSoup

def delete_zfile(zfile):
    """ Proper deletion of a ZFile. This removed all associated database objects as well as preview images and the zipfile from disk.
        This function does not recalculate the queue size afterwards if an unpublished ZFile is deleted. """
    output = []
    output.append("Removing ZFile `{}`.".format(str(zfile)))

    # Remove the physical file
    path = zfile.phys_path()
    if os.path.isfile(path):
        os.remove(path)
        output.append("Removed physical file.")
    else:
        output.append("No physical file to remove.")

    # Remove the Upload object
    if zfile.upload:
        zfile.upload.delete()
        output.append("Removed Upload object")
    else:
        output.append("No Upload object to remove.")

    # Remove the preview image
    screenshot_path = zfile.screenshot_phys_path()
    if screenshot_path and os.path.isfile(screenshot_path):
        os.remove(screenshot_path)
        output.append("Removed preview image.")
    else:
        output.append("No preview image to remove.")

    # Remove the contents objects
    content = zfile.content.all()
    if content:
        for c in content:
            c.delete()
        output.append("Removed Content object(s).")
    else:
        output.append("No Content objects to remove.")

    # Remove the download objects
    downloads = zfile.downloads.all()
    if downloads:
        for d in downloads:
            d.delete()
        output.append("Removed Download object(s).")
    else:
        output.append("No Download objects to remove.")

    # Remove the file object
    zfile.delete()
    output.append("Removed ZFile object")
    return output


def delete_feedback(feedback):
    """ Proper deletion of Feedback. This removes the item from the database, as well as recalculating counts and scores on the associated file. """
    output = []
    feedback.delete()
    output.append("Removed Feedback object")
    if feedback.zfile:
        feedback.zfile.calculate_feedback()
        output.append("Recalculated ZFile's feedback count")
        feedback.zfile.calculate_reviews()
        output.append("Recalculated ZFile's review count and rating")
        feedback.zfile.save()
        output.append("Saved ZFile")
    return output



def get_article_word_count(article):
        rendered = article.render()

        if article.schema == "html" or article.schema == "django":
            soup = BeautifulSoup(rendered, "html.parser")
            rendered = soup.get_text()

        words = rendered.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").split(" ")
        count = 0
        for word in words:
            if word.strip() != "":
                count += 1

        return count

def get_article_urls(article, domain=""):
    output = []

    raw = []
    if article.schema in ["html", "django"]:
        soup = BeautifulSoup(article.content, "html.parser")

        for tag in soup.find_all("a"):
            raw.append(tag.get("href"))

    for r in raw:
        if r.startswith("{%"):
            tag = r.split(" ")
            if len(tag) > 4:
                # print("HEY WEIRD TAG ALERT", self.id, self.title, tag)
                output.append("!!SKIPME!! " + r)
        else:
            output.append(r)

    if domain:
        output = list(map(lambda o: domain + o if (not o.startswith("http") and not o.startswith("mailto")) else o, output))
    output.sort()

    return output
