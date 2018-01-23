# GetFund
测试读取基金数据,生成RSS

# 安装 crontab
# yum install crontabs

# 设定服务
# systemctl enable crond
# systemctl start crond

crontab -e配置是针对某个用户的，而编辑/etc/crontab是针对系统的任务 

查看调度任务 
crontab -l //列出当前的所有调度任务 
crontab -l -u jp //列出用户jp的所有调度任务 

删除任务调度工作 
crontab -r //删除所有任务调度工作 

# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name command to be executed

星号（*）：代表所有可能的值，例如month字段如果是星号，则表示在满足其它字段的制约条件后每月都执行该命令操作。 
逗号（,）：可以用逗号隔开的值指定一个列表范围，例如，“1,2,5,7,8,9” 
中杠（-）：可以用整数之间的中杠表示一个整数范围，例如“2-6”表示“2,3,4,5,6” 
正斜线（/）：可以用正斜线指定时间的间隔频率，例如“0-23/2”表示每两小时执行一次。同时正斜线可以和星号一起使用，例如*/10，如果用在minute字段，表示每十分钟执行一次。
