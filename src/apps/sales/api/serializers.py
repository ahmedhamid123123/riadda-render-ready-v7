from rest_framework import serializers

class ReceiptSerializer(serializers.Serializer):
	transaction_id = serializers.IntegerField()
	company = serializers.CharField()
	denomination = serializers.CharField()
	confirmed_at = serializers.CharField(allow_null=True)


class SellResponseSerializer(serializers.Serializer):
	transaction_id = serializers.IntegerField()
	company = serializers.CharField()
	denomination = serializers.CharField()
	price = serializers.CharField()


class SellInputSerializer(serializers.Serializer):
	denomination_id = serializers.IntegerField()


class TransactionItemSerializer(serializers.Serializer):
	id = serializers.IntegerField()
	company = serializers.CharField()
	denomination = serializers.CharField()
	status = serializers.CharField()
	price = serializers.CharField()
	confirmed_at = serializers.CharField(allow_null=True)
	receipt_token = serializers.CharField(allow_null=True)
	created_at = serializers.CharField(allow_null=True)


class TransactionListSerializer(serializers.Serializer):
	page = serializers.IntegerField()
	total_pages = serializers.IntegerField()
	total_count = serializers.IntegerField()
	results = TransactionItemSerializer(many=True)


class ReissueResponseSerializer(serializers.Serializer):
	transaction_id = serializers.IntegerField()
	receipt_token = serializers.CharField()
	receipt_url = serializers.CharField()
	reissue_count = serializers.IntegerField()
	reissue_limit = serializers.IntegerField()

