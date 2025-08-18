from datetime import datetime

from django.shortcuts import render

from museum_site.settings import REMOTE_ADDR_HEADER
from .models import Poll, Option, Vote


def index(request, poll_id=None):
    context = {}

    if poll_id is None:
        poll = Poll.objects.all().order_by("-id")[0]
    else:
        poll = Poll.objects.get(pk=poll_id)
        context["show_results"] = True
    context["all_votes"] = Vote.objects.filter(poll_id=poll_id).order_by("-id")

    # Add vote if necessary
    if request.POST.get("action") == "Vote" and poll.active and request.POST.get("vote") and request.POST.get("email"):
        vote = Vote(
            ip=request.META[REMOTE_ADDR_HEADER],
            timestamp=datetime.now(),
            email=request.POST["email"],
            option_id=int(request.POST["vote"]),
            poll_id=poll.pk
        )
        vote.save()

    past_polls = Poll.objects.all().order_by("-id")

    # Final Votes
    final_votes = []
    final_votes_dict = {}
    for v in context["all_votes"]:
        if final_votes_dict.get(v.email) is None:
            final_votes_dict[v.email] = v
    for email, vote in final_votes_dict.items():
        final_votes.append(vote)


    context["final_votes"] = final_votes
    context["poll"] = poll
    context["title"] = poll.title
    context["past_polls"] = past_polls
    context["meta_context"] = {
    "description": ["name", "A patron exclusive poll for which ZZT world should receive a Closer Look article"],
    "og:title": ["property", context["title"] + " - Museum of ZZT"],
    "og:image": ["property", "pages/poll.png"]
    }
    return render(request, "poll/index.html", context)
