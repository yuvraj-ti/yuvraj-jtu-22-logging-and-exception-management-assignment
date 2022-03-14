import sagemaker

from fast_api_als.utils.aws_sagemaker import get_sagemaker_client
from sagemaker.serializers import CSVSerializer
from sagemaker.deserializers import JSONDeserializer

sagemaker_client = get_sagemaker_client()


def get_predictor(endpoint_name):
    predictor = sagemaker.predictor.Predictor(
        endpoint_name,
        sagemaker_session=sagemaker.session.Session(sagemaker_client)
    )
    predictor.serializer = CSVSerializer()
    predictor.deserializer = JSONDeserializer()
    return predictor