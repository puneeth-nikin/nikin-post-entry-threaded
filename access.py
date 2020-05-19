#!/usr/bin/env python3

import logging
from kiteconnect import KiteConnect

logging.basicConfig(level=logging.DEBUG)

kite = KiteConnect(api_key="7lwrah449p8wk3i0")


data = kite.generate_session(request_token="y6MJo7GWAOzQ5OSfb7aiMBjQYkOauWdr", api_secret="fgnjqolrw9vtk20jijz6pcd7uy79vgup")
print(data["access_token"])

