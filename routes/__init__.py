from flask import Blueprint
from .GET_orders import orders_bp
from .POST_input_order import post_input_order_bp
from .UPDATE_tablePesanan import update_order_bp
from .DELETE_allDelete import delete_order_bp
from .UPDATE_fromDesigner import update_design_bp
from .UPDATE_fromProduction import sync_prod_bp
from .UPDATE_table_urgent import update_urgent_bp
from .POST_table_urgent import post_urgent_bp
from .note_operations import note_bp


from .Ai_ChatBot.services.whatAppChat import whatsapp_bp, init_scheduler


api_bp = Blueprint('api', __name__)

# Register core blueprints
api_bp.register_blueprint(orders_bp)
api_bp.register_blueprint(post_input_order_bp)
api_bp.register_blueprint(update_order_bp)
api_bp.register_blueprint(delete_order_bp)
api_bp.register_blueprint(update_design_bp)
api_bp.register_blueprint(sync_prod_bp)
api_bp.register_blueprint(update_urgent_bp)
api_bp.register_blueprint(post_urgent_bp)
api_bp.register_blueprint(note_bp)


api_bp.register_blueprint(whatsapp_bp)
init_scheduler()

