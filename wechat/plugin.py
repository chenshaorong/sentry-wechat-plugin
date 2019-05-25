# -*- coding: utf-8 -*-
import json

from datetime import datetime
from pytz import timezone
import requests
import pkg_resources
from django import forms
from sentry.plugins.bases.notify import NotificationPlugin


class WeChatForm(forms.Form):
    agentid = forms.IntegerField(help_text=u"企业应用的id，整型。可在应用的设置页面查看")
    corpid = forms.CharField(help_text=u"查看：企业微信=>我的企业=>企业ID")
    corpsecret = forms.CharField(help_text=u"查看：企业微信=>我的企业=>权限管理=>管理组，选择要告警的组，最下面有个Secret，记得要提前添加好管理范围和权限信息")
    touser = forms.CharField(
        help_text=u"成员ID列表（消息接收者，多个接收者用‘|’分隔，最多支持1000个）。特殊情况：指定为@all，则向关注该企业应用的全部成员发送",
        required=False,
    )
    toparty = forms.CharField(
        help_text=u"部门ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数",
        required=False,
    )
    totag = forms.CharField(
        help_text=u"标签ID列表，多个接收者用‘|’分隔，最多支持100个。当touser为@all时忽略本参数",
        required=False,
    )
    host = forms.CharField(
        help_text=u"Sentry访问的Host(填真实访问的地址，生产一般由Nginx、Apache进行反代，用于发送消息时点击href直接跳转到event页面)，如：http://127.0.0.1:9000",
        required=False,
    )
    safe = forms.BooleanField(help_text=u"表示是否是保密消息，0表示否，1表示是，默认0", required=False)


class WeChatPlugin(NotificationPlugin):
    # Generic plugin information
    title = 'wechat'
    slug = 'wechat'
    description = u'Sentry微信告警插件'
    version = pkg_resources.get_distribution("sentry_wechat_plugin").version
    author = 'shaorong.chen'
    author_url = 'https://github.com/chenshaorong'
    resource_links = [
        ('Source', 'https://github.com/chenshaorong/sentry-wechat-plugin'),
    ]

    # Configuration specifics
    conf_key = slug
    conf_title = title

    project_conf_form = WeChatForm

    # Should this plugin be enabled by default for projects?
    # project_default_enabled = False

    def is_configured(self, project):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option('agentid', project) and
                    self.get_option('corpid', project) and
                    self.get_option('corpsecret', project))

    def notify_users(self, group, event, *args, **kwargs):
        if not self.is_configured(group.project):
            return

        project = event.project
        agentid = self.get_option("agentid", project)
        corpid = self.get_option("corpid", project)
        corpsecret = self.get_option("corpsecret", project)
        touser = self.get_option("touser", project)
        toparty = self.get_option("toparty", project)
        totag = self.get_option("totag", project)
        host = self.get_option("host", project) or ''
        safe = self.get_option("safe", project)

        access_token = requests.get(
            'https://qyapi.weixin.qq.com/cgi-bin/gettoken',
            params={"corpid": corpid, "corpsecret": corpsecret}
        ).json().get("access_token")
        if not access_token:
            return u'请检查agentid、corpid、corpsecret是否设置正确'

        message = {
            "msgtype": "text",
            "agentid": agentid,
            "touser": touser,
            'toparty': toparty,
            'totag': totag,
            'safe': '1' if safe else '0',
            "text": {
                "content": '[标题] {}\n[时间] {}\n[{}] {}\n[href]({})'.format(
                    "Sentry {} 项目告警".format(project.slug),
                    datetime.now(timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S"),
                    event.get_tag('level').capitalize(), event.message.encode('utf8'),
                    "{}{}events/{}/".format(host, group.get_absolute_url(), event.id),
                )
            }
        }

        return requests.post(
            'https://qyapi.weixin.qq.com/cgi-bin/message/send',
            params={"access_token": access_token},
            data=json.dumps(message),
        )
