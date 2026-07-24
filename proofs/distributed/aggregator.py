import time, json, urllib.request

NODES = [
    "http://node1:8000/v1/decision",
    "http://node2:8000/v1/decision",
    "http://node3:8000/v1/decision",
    "http://node4:8000/v1/decision",
]

def post(url, payload):
    data=json.dumps(payload).encode("utf-8")
    req=urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))

def consensus(responses):
    counts={}
    for r in responses:
        d=r.get("decision")
        counts[d]=counts.get(d,0)+1
    best=max(counts.items(), key=lambda x:x[1])
    if best[1] >= 3:
        return {"decision": best[0], "votes": counts, "responses": responses}
    return {"decision": "BLOCK", "votes": counts, "responses": responses, "reason":"no 3/4 supermajority"}

def main():
    payload={
      "metrics":{"T_mean":0.2,"H_score":0.3,"A_score":0.1,"S":0.25},
      "theta_S":0.25,
      "nonce":"distributed-demo-1"
    }
    time.sleep(3)
    responses=[post(url,payload) for url in NODES]
    print(json.dumps(consensus(responses), indent=2))

if __name__=="__main__":
    main()
