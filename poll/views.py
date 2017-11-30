from datetime import datetime

from django.shortcuts import render

from .models import Poll, Option, Vote

def index(request, poll_id=None):
    data = {}

    data["polls"] = Poll.objects.all().order_by("-id")
    if poll_id is None:
        data["display_poll"] = data["polls"][0]
        data["results_mode"] = False
    else:
        data["display_poll"] = Poll.objects.get(pk=int(poll_id))
        data["results_mode"] = True

    # Add vote if necessary
    if request.POST.get("action") == "Vote" and data["display_poll"].active and request.POST.get("vote") and request.POST.get("email"):
        vote = Vote(ip=request.META["REMOTE_ADDR"], timestamp=datetime.now(), email=request.POST["email"], option_id=int(request.POST["vote"]), poll_id=data["display_poll"].id)
        vote.save()
        data["results_mode"] = True

    # Calculate the winner
    if data["results_mode"]:
        results = [0,0,0,0,0]

        votes = Vote.objects.filter(poll_id=poll_id).order_by("id")

        voters = {}

        for vote in votes:
            voters[vote.email] = vote.option_id

        for k in voters.keys():
            if data["display_poll"].option1_id == voters[k]:
                results[0] += 1
            if data["display_poll"].option2_id == voters[k]:
                results[1] += 1
            if data["display_poll"].option3_id == voters[k]:
                results[2] += 1
            if data["display_poll"].option4_id == voters[k]:
                results[3] += 1
            if data["display_poll"].option5_id == voters[k]:
                results[4] += 1

        data["results"] = results
        data["winner"] = max(results)

    return render(request, "poll/index.html", data)
