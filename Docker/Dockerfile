FROM henryxiaoyang/wechat-box:3.9.5.81

# clear /payloads
RUN sudo rm -rf /payloads

COPY root/ /

# init with GUI
RUN bash -c 'nohup /entrypoint.sh 2>&1 &' && sleep 5 && /payloads.sh \
    && sudo cp -r /wechat-etc/* /etc/ \
    && sudo rm /tmp/.X0-lock
#settings

ENTRYPOINT ["/wx-entrypoint.sh"]