def test_user_data_is_isolated(client):
    assert client.post('/watchlist/thyao',headers={'X-Demo-User':'demo-user'}).status_code==201
    assert client.get('/watchlist',headers={'X-Demo-User':'other'}).status_code==403
def test_demo_flow(client):
    h={'X-Demo-User':'demo-user'}; assert client.get('/instruments',headers=h).json()
    assert client.post('/watchlist/thyao',headers=h).status_code==201
    quote=client.get('/instruments/thyao/quote',headers=h).json()
    payload={'instrument_id':'thyao','kind':'percent_drop','percent':'5','reference_value':quote['value'],'reference_source':'current_quote','reference_at':quote['as_of']}
    assert client.post('/alarms',headers=h,json=payload).status_code==201
    result=client.get('/instruments/thyao/forecast',headers=h).json(); assert result['oneDay']['available']; assert result['explanation']['sourceIds']
