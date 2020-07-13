-- Your SQL goes here
create view user_view as 
select id,
username,
username as acct,
name,
status as note,
is_private as locked,
avatar_url as avatar,
header_url as header,
followers_count,
following_count,
statuses_count
from user_profile join user_ on user_profile.user_id=user_.id;