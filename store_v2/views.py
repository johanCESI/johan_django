from django.shortcuts import render, get_object_or_404

from .models import Album, Artist, Contact, Booking

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .forms import ContactForm, ParagraphErrorList

def index(request):
    albums = Album.objects.filter(available=True).order_by('-created_at')[:12]
    context = {
        'albums': albums
    }
    return render(request, 'store/index.html', context)

def listing(request):
    albums_list = Album.objects.filter(available=True)
    # Slice pages
    paginator = Paginator(albums_list, 9)
    # Get current page number
    page = request.GET.get('page')
    # Return only this page albums and not others
    try:
        albums = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        albums = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        albums = paginator.page(paginator.num_pages)
    context = {
        'albums': albums,
        'paginate': True
    }
    return render(request, 'store/listing.html', context)

def detail(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    artists = [artist.name for artist in album.artists.all()]
    artists_name = " ".join(artists)
    context = {
        'album_title': album.title,
        'artists_name': artists_name,
        'album_id': album.id,
        'thumbnail': album.picture,
    }
    if request.method == 'POST':
        form = ContactForm(request.POST, error_class=ParagraphErrorList)
        if form.is_valid():
            # Form is correct.
            # We can proceed to booking.
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']
            contact = Contact.objects.filter(email=email)
            if not contact.exists():
                # If a contact is not registered, create a new one.
                contact = Contact.objects.create(
                    email=email,
                    name=name
                )
            else:
                contact = contact.first()

            # If no album matches the id, it means the form must have been tweaked
            # so returning a 404 is the best solution.
            album = get_object_or_404(Album, id=album_id)
            booking = Booking.objects.create(
                contact=contact,
                album=album
            )

            # Make sure no one can book the album again.
            album.available = False
            album.save()
            context = {
                'album_title': album.title
            }
            return render(request, 'store/merci.html', context)
        else:
            # Form data doesn't match the expected format.
            # Add errors to the template.
            context['errors'] = form.errors.items()
    else:
        # GET method. Create a new form to be used in the template.
        form = ContactForm()
    context['form'] = form
    return render(request, 'store/detail.html', context)

def search(request):
    query = request.GET.get('query')
    if not query:
        albums = Album.objects.all()
    else:
        # title contains the query is and query is not sensitive to case.
        albums = Album.objects.filter(title__icontains=query)
    if not albums.exists():
        albums = Album.objects.filter(artists__name__icontains=query)
    title = "Résultats pour la requête %s"%query
    context = {
        'albums': albums,
        'title': title
    }
    return render(request, 'store/search.html', context)