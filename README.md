## **Home Assistant Ring integration (modified)**

[https://www.home-assistant.io/integrations/ring/](https://www.home-assistant.io/integrations/ring/)

**Note:** This modified integration repo is temporary, while waiting for my [PR](https://github.com/home-assistant/core/pull/91600) to be merged.

[Ring](./screenshot.png)

## **Addtional features**

- Add Ring Intercom support:
    - Change microphone gain
    - Change speaker volume
    - Open door button
    - Battery sensor
    - Status sensor


## **Installation**

Just download this repository from [here](https://github.com/MartinPham/ring-integration-modified/archive/refs/heads/master.zip), extract and copy paste the content of the ``custom_components/ring_martinpham`` folder into your ``config/custom_components`` directory. As example, you will get the ``manifest.json`` file in the following path: ``/config/custom_components/ring_martinpham/manifest.json``.



## **Credits**

- Original **[python-ring-doorbell](https://github.com/tchellomello/python-ring-doorbell)** library from **[tchellomello](https://github.com/tchellomello)**
- **[Intercom PR](https://github.com/tchellomello/python-ring-doorbell/pull/277)** from **[rautsch](https://github.com/rautsch)**
- Original **[ring integration](https://github.com/home-assistant/core/tree/dev/homeassistant/components/ring)** from **[home-assistant/core](https://github.com/home-assistant/core)**