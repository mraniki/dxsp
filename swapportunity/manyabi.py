import many_abis as ma

print(ma.ALL_ABIS_NAME)
print(ma.ABIS)
chains = ma.all_chains()
print(chains)
bsc = ma.chain(chain_id=56)
print(bsc['chain_id'])
print(bsc['rpc'][0])