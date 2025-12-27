from sentinelhub import SHConfig

config = SHConfig()
config.sh_client_id = 'You can get your own client ID at the Copernicus website'
config.sh_client_secret = 'You can get your own client secret from the Copernicus website'
config.sh_base_url = 'https://sh.dataspace.copernicus.eu'
config.sh_token_url = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'

from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    DownloadRequest,
    MimeType,
    MosaickingOrder,
    SentinelHubDownloadClient,
    SentinelHubRequest,
    bbox_to_dimensions,
)

from utils import plot_image
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import matplotlib.pyplot as plt

def get_city_coordinates(city_name):
    geolocator = Nominatim(user_agent="city_boundary_box_calculator")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"City '{city_name}' not found")

def calculate_boundary_box(latitude, longitude, width_km):
    half_width_km = width_km / 2.0
    north = geodesic(kilometers=half_width_km).destination((latitude, longitude), 0).latitude
    south = geodesic(kilometers=half_width_km).destination((latitude, longitude), 180).latitude
    east = geodesic(kilometers=half_width_km).destination((latitude, longitude), 90).longitude
    west = geodesic(kilometers=half_width_km).destination((latitude, longitude), 270).longitude
    return west, south, east, north

def get_boundary_box(city_name, width_km):
    latitude, longitude = get_city_coordinates(city_name)
    west, south, east, north = calculate_boundary_box(latitude, longitude, width_km)
    bbox = BBox(bbox=[(west, south), (east, north)], crs=CRS.WGS84)
    return bbox

# Enter city
city_name = "Kalasatama"
# Enter resolution (km)
resolution = 10

bb_bbox = get_boundary_box(city_name, resolution)

bb_size = bbox_to_dimensions(bb_bbox, resolution=resolution)

print(f"Image shape at {resolution} m resolution: {bb_size} pixels")

evalscript_ndvi = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08"],
    output:{
      id: "default",
      bands: 2,
      sampleType: SampleType.FLOAT32
    }
  }
}

function evaluatePixel(sample) {
  return [sample.B04, sample.B08]
}
"""
# Define two time intervals to compare
time_intervals = [
    ("2017-06-10", "2017-08-10"),  # First time period
    ("2023-06-10", "2023-08-10")   # Second time period
]

ndvi_data_list = []

for time_interval in time_intervals:
    ndvi_request = SentinelHubRequest(
        evalscript=evalscript_ndvi,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A.define_from("s2l2a", service_url=config.sh_base_url),
                time_interval=time_interval,
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bb_bbox,
        size=bb_size,
        config=config,
    )

    ndvi_data = ndvi_request.get_data()
    b04 = ndvi_data[0][:, :, 0]  
    b08 = ndvi_data[0][:, :, 1] 

    ndvi = (b08 - b04) / (b08 + b04)
    ndvi_data_list.append(ndvi)

fig, axes = plt.subplots(1, 2, figsize=(20, 10))

axes[0].imshow(ndvi_data_list[0], cmap='RdYlGn', vmin=-1, vmax=1)
axes[0].set_title(f"NDVI for {time_intervals[0][0]} to {time_intervals[0][1]}")
axes[0].axis('off')

axes[1].imshow(ndvi_data_list[1], cmap='RdYlGn', vmin=-1, vmax=1)
axes[1].set_title(f"NDVI for {time_intervals[1][0]} to {time_intervals[1][1]}")
axes[1].axis('off')

fig.colorbar(plt.cm.ScalarMappable(cmap='RdYlGn', norm=plt.Normalize(vmin=-1, vmax=1)), ax=axes, orientation='horizontal', fraction=0.05, pad=0.1, label="NDVI")
plt.suptitle("NDVI Comparison for Different Time Periods")
plt.show()