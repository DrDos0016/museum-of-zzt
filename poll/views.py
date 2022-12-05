from datetime import datetime

from django.shortcuts import render

from .models import Poll, Option, Vote

def index(request, poll_id=None):
    data = {}


    data["polls"] = Poll.objects.all().order_by("-id")
    if poll_id is None:
        data["display_poll"] = data["polls"][0]

        # Load up the results if the poll has ended already
        if not data["display_poll"].active:
            data["results_mode"] = True
        else:
            data["results_mode"] = False
    else:
        data["display_poll"] = Poll.objects.get(pk=int(poll_id))
        data["results_mode"] = True

    data["title"] = data["display_poll"].title

    data["poll_zfiles"] = (
        data["display_poll"].option1.file,
        data["display_poll"].option2.file,
        data["display_poll"].option3.file,
        data["display_poll"].option4.file,
        data["display_poll"].option5.file
    )

    # Add vote if necessary
    if request.POST.get("action") == "Vote" and data["display_poll"].active and request.POST.get("vote") and request.POST.get("email"):
        vote = Vote(ip=request.META["REMOTE_ADDR"], timestamp=datetime.now(), email=request.POST["email"], option_id=int(request.POST["vote"]), poll_id=data["display_poll"].id)
        vote.save()
        data["results_mode"] = True

    # Calculate the winner
    if data["results_mode"]:
        results = [0,0,0,0,0]

        votes = Vote.objects.filter(poll_id=data["display_poll"].id).order_by("-id")

        data["all_votes"] = votes
        data["final_votes"] = []
        observed_emails = []

        for v in votes:
            if v.email not in observed_emails:
                observed_emails.append(v.email)
                data["final_votes"].append(v)

                if data["display_poll"].option1_id == v.option_id:
                    results[0] += 1
                elif data["display_poll"].option2_id == v.option_id:
                    results[1] += 1
                elif data["display_poll"].option3_id == v.option_id:
                    results[2] += 1
                elif data["display_poll"].option4_id == v.option_id:
                    results[3] += 1
                elif data["display_poll"].option5_id == v.option_id:
                    results[4] += 1

        data["results"] = results
        data["winner"] = max(results)

    data["meta_context"] = {
        "description": ["name", "A patron exclusive poll for which ZZT world should receive a Closer Look article"],
        "og:title": ["property", data["title"] + " - Museum of ZZT"],
        "og:image": ["property", "pages/poll.png"]
    }
    return render(request, "poll/index.html", data)
