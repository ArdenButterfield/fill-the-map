from detectree2.preprocessing.tiling import tile_data
from detectree2.models.outputs import project_to_geojson, stitch_crowns, clean_crowns
from detectree2.models.predict import predict_on_data
from detectree2.models.train import setup_cfg
from detectron2.engine import DefaultPredictor
import rasterio

tiles_path = './'
trained_model = "./230103_randresize_full.pth"
cfg = setup_cfg(update_model=trained_model)
predict_on_data(tiles_path, predictor=DefaultPredictor(cfg))
# project_to_geojson(tiles_path, tiles_path + "predictions/", tiles_path + "predictions_geo/")