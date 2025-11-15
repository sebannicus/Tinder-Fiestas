
from django.contrib import admin
from .models import UserProfile, CheckIn, Event, EventAttendance, WalletUser


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('wallet_address', 'username', 'created_at', 'total_checkins')
    search_fields = ('wallet_address', 'username')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
    def total_checkins(self, obj):
        return obj.checkins.count()
    total_checkins.short_description = 'Total Check-ins'


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'latitude', 'longitude', 'timestamp', 'tx_hash_short')
    search_fields = ('user__wallet_address', 'location', 'tx_hash')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'tx_hash')
    
    def tx_hash_short(self, obj):
        return f"{obj.tx_hash[:10]}..." if len(obj.tx_hash) > 10 else obj.tx_hash
    tx_hash_short.short_description = 'TX Hash'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'start_date', 'end_date', 'total_attendees', 'status')
    search_fields = ('name', 'location', 'description')
    list_filter = ('start_date', 'created_at')
    ordering = ('-start_date',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description')
        }),
        ('Ubicación', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date', 'created_at')
        }),
    )
    
    def total_attendees(self, obj):
        return obj.attendees.count()
    total_attendees.short_description = 'Asistentes'
    
    def status(self, obj):
        from django.utils import timezone
        now = timezone.now()
        if obj.end_date < now:
            return "🔴 Finalizado"
        elif obj.start_date > now:
            return "🟡 Próximo"
        else:
            return "🟢 En Curso"
    status.short_description = 'Estado'


@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'timestamp', 'tx_hash_short')
    search_fields = ('user__wallet_address', 'event__name', 'tx_hash')
    list_filter = ('timestamp', 'event')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'tx_hash')
    
    def tx_hash_short(self, obj):
        return f"{obj.tx_hash[:10]}..." if len(obj.tx_hash) > 10 else obj.tx_hash
    tx_hash_short.short_description = 'TX Hash'


@admin.register(WalletUser)
class WalletUserAdmin(admin.ModelAdmin):
    list_display = ('address', 'last_login')
    search_fields = ('address',)
    list_filter = ('last_login',)
    ordering = ('-last_login',)
    readonly_fields = ('last_login',)