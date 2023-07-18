from datetime import datetime

from rest_framework import serializers

from books.serializers import BookBorrowingSerializer
from borrowings.models import Borrowing


class ReadBorrowingSerializer(serializers.ModelSerializer):
    book = BookBorrowingSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
            "actual_return_date"
        )
        # TODO: remove actual_return_date


class CreateBorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("expected_return_date", "book")

    def validate_book(self, value):
        """
        Check that the book inventory is more than zero.
        """
        if value.inventory == 0:
            raise serializers.ValidationError(
                f'No "{value.title}" books left'
            )
        return value

    def validate_expected_return_date(self, value):
        """
        Ensure that the user is unable to set
        the return date to a time in the past.
        """
        if value < datetime.now().date():
            raise serializers.ValidationError(
                f"You can't set the return date before today"
            )
        return value

    def create(self, validated_data):
        """
        If a new Borrowing instance created,
        subtract one book from book.inventory.
        """
        borrowing = Borrowing.objects.create(
            **validated_data
        )
        book = borrowing.book
        book.inventory -= 1
        book.save()
        return borrowing


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = "__all__"


class EmptySerializer(serializers.Serializer):
    pass
