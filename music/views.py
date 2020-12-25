from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from .models import Song, Watchlater, Channel, History,User,Artist,Genre
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.db.models import Case, When
from django.contrib import messages
from django.urls import reverse


def home(request):
    context = {
        'artists': Artist.objects.all(),
        'genres': Genre.objects.all()[:6],
        'latest_songs': Song.objects.all()[:6]
    }
    return render(request, "music/index.html", context)


def songs(request):
    song = Song.objects.all()
    return render(request, "music/song.html", {"song": song})


def songpost(request, id):
    song = Song.objects.filter(song_id=id).first()
    recommendTag = Song.objects.filter(tags=song.tags)
    recommendSinger = Song.objects.filter(tags=song.singer)
    totalLikes = song.total_likes
    liked = False
    if song.likes.filter(id=request.user.id).exists():
        liked = True
    return render(
        request,
        "music/songpost.html",
        {
            "song": song,
            "tag": recommendTag,
            "singer": recommendSinger,
            "totalLikes": totalLikes,
            "liked": liked,
        },
    )


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("/muzik")

    return render(request, "music/login.html")


def signup(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]

        if User.objects.filter(username=username).exists():
            messages.error(
                request, "Username is already taken. Please try another one !"
            )

        if len(username) > 15:
            messages.error(request, "Username must be less than 15 characters")

        if not username.isalnum():
            messages.error(request, "Username should only contain Letters and Numbers.")

        if pass1 != pass2:
            messages.error(request, "Password Do not Match. Please Sign Up Again")

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = first_name
        myuser.last_name = last_name
        myuser.save()
        user = authenticate(username=username, password=pass1)
        from django.contrib.auth import login

        login(request, user)

        channel = Channel(name=username)
        channel.save()

        return redirect("/muzik")

    return render(request, "music/signup.html")


def logout_user(request):
    logout(request)
    return redirect("/muzik")


def channel(request, channel):
    chan = Channel.objects.filter(name=channel).first()
    video_ids = str(chan.music).split(" ")[1:]

    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(video_ids)])
    song = Song.objects.filter(song_id__in=video_ids).order_by(preserved)

    return render(request, "music/channel.html", {"channel": chan, "song": song})


def upload(request):
    if request.method == "POST":
        name = request.POST["name"]
        singer = request.POST["singer"]
        tag = request.POST["tag"]
        image = request.POST["image"]
        song1 = request.FILES["file"]

        song_model = Song(name=name, singer=singer, tags=tag, image=image, song=song1,)
        song_model.save()

        music_id = song_model.song_id
        channel_find = Channel.objects.filter(name=str(request.user))
        print(channel_find)

        for i in channel_find:
            i.music += f" {music_id}"
            i.save()

    return render(request, "music/upload.html")


def history(request):
    if request.method == "POST":
        user = request.user
        music_id = request.POST["music_id"]
        history = History(user=user, music_id=music_id)
        history.save()

        return redirect(f"/muzik/songs/{music_id}")

    history = History.objects.filter(user=request.user)
    ids = []
    for i in history:
        ids.append(i.music_id)

    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    song = Song.objects.filter(song_id__in=ids).order_by(preserved)

    return render(request, "music/history.html", {"history": song})


def watchlater(request):
    if request.method == "POST":
        user = request.user
        video_id = request.POST["video_id"]

        watch = Watchlater.objects.filter(user=user)

        for i in watch:
            if video_id == i.video_id:
                message = "Your Video is Already Added"
                break
        else:
            watchlater = Watchlater(user=user, video_id=video_id)
            watchlater.save()
            message = "Your Video is Succesfully Added"

        song = Song.objects.filter(song_id=video_id).first()
        return render(
            request, f"music/songpost.html", {"song": song, "message": message}
        )

    wl = Watchlater.objects.filter(user=request.user)
    ids = []
    for i in wl:
        ids.append(i.video_id)

    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    song = Song.objects.filter(song_id__in=ids).order_by(preserved)

    return render(request, "music/watchlater.html", {"song": song})


def history(request):
    if request.method == "POST":
        user = request.user
        music_id = request.POST["song_id"]
        history = History(user=user, music_id=music_id)
        history.save()

        return redirect(f"/muzik/songs/{music_id}")

    history = History.objects.filter(user=request.user)
    ids = []
    for i in history:
        ids.append(i.music_id)

    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    song = Song.objects.filter(song_id__in=ids).order_by(preserved)

    return render(request, "music/history.html", {"history": song})


def search(request):
    query = request.GET.get("query")
    print(query)
    song = Song.objects.filter(name__icontains=query)
    print(song)
    return render(request, "music/search.html", {"songs": song})


def LikeView(request, pk):
    song = get_object_or_404(Song, song_id=request.POST.get("song_id"))
    liked = False
    if song.likes.filter(id=request.user.id).exists():
        song.likes.remove(request.user)
        liked = False
    else:
        song.likes.add(request.user)
        liked = True
    return HttpResponseRedirect(reverse("songpost", args=[str(pk)]))

