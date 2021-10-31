from django.contrib import admin
from .models import Document, MovementOfDocument, ReplyDocument, FileReplyDocument, FileDocument, Statement


class MovementOfDocumentInline(admin.TabularInline):
    model = MovementOfDocument
    extra = 0


class FileReplyDocumentInline(admin.TabularInline):
    model = FileReplyDocument
    extra = 0


class FileDocumentInline(admin.TabularInline):
    model = FileDocument
    extra = 0


@admin.register(Statement)
class AdminStatement(admin.ModelAdmin):
    list_display = ('number', 'author', 'type', 'status', 'director', 'responsible', 'created', 'updated')


@admin.register(Document)
class AdminDocument(admin.ModelAdmin):
    list_display = ('number', 'author', 'name', 'status', 'created', 'updated')
    inlines = [MovementOfDocumentInline, FileDocumentInline]


@admin.register(MovementOfDocument)
class AdminMovementOfDocument(admin.ModelAdmin):
    list_display = ('responsible', 'document', 'status', 'created', 'updated')


@admin.register(ReplyDocument)
class AdminReplyDocument(admin.ModelAdmin):
    list_display = ('movement', 'status', 'created', 'updated')
    inlines = [FileReplyDocumentInline]
