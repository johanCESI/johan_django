from django.contrib import admin
from .models import Booking, Contact, Album, Artist
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

class AdminURLMixin(object):
    def get_admin_url(self, obj):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        return reverse("admin:store_v2_%s_change" % (
            content_type.model),
            args=(obj.id,))

class BookingInline(admin.TabularInline, AdminURLMixin):
    verbose_name = "Réservation"
    verbose_name_plural = "Réservations"
    model = Booking
    readonly_fields = ["created_at", "album_link", "contacted"]
    fields = ["created_at", "album_link", "contacted"]

    def album_link(self, booking):
        url = self.get_admin_url(booking.album)
        return mark_safe("<a href='{}'>{}</a>".format(url, booking.album.title))

    def has_add_permission(self, request):
        return False
    
    album_link.short_description = "Album"

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    inlines = [BookingInline,] # list of bookings made by a contact
    extra = 0

class AlbumArtistInline(admin.TabularInline):
    verbose_name = "Disque"
    verbose_name_plural = "Disques"
    model = Album.artists.through # the query goes through an intermediate table.
    extra = 1


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    inlines = [AlbumArtistInline,]

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    search_fields = ['reference', 'title']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin, AdminURLMixin):
    list_filter = ['created_at', 'contacted']
    fields = ["created_at", "contact_link", 'album_link', 'contacted']
    readonly_fields = ["created_at", "contact_link", "album_link", "contacted"]

    def contact_link(self, booking):
        url = self.get_admin_url(booking.contact)
        return mark_safe("<a href='{}'>{}</a>".format(url, booking.contact.name))

    def album_link(self, booking):
        url = self.get_admin_url(booking.album)
        return mark_safe("<a href='{}'>{}</a>".format(url, booking.album.title))

#admin.site.register(Booking)