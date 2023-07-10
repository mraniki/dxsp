
<table style="border: 1px solid transparent">
  <tr>
    <td>
<a href="https://talkytrader.github.io/wiki/"><img src="https://img.shields.io/badge/Wiki-%23000000.svg?style=for-the-badge&logo=wikipedia&logoColor=white"></a><br>
<a href="https://github.com/mraniki/dxsp/"><img src="https://img.shields.io/badge/github-%23000000.svg?style=for-the-badge&logo=github&logoColor=white"></a>
<a href="https://hub.docker.com/r/mraniki/tt"><img src="https://img.shields.io/docker/pulls/mraniki/tt?style=for-the-badge"></a><br>
<a href="https://coindrop.to/mraniki"><img src="https://img.shields.io/badge/tips-000000?style=for-the-badge&logo=buymeacoffee&logoColor=white"></a>
<a href="https://t.me/TTTalkyTraderChat/1"><img src="https://img.shields.io/badge/talky-blue?style=for-the-badge&logo=telegram&logoColor=white"></a>
<a href="https://discord.gg/gMNERs5M9"><img src="https://img.shields.io/discord/1049307055867035648?style=for-the-badge&logo=discord&logoColor=white&label=%20%20&color=blue"></a>
  </td>
    <td align="center"><img width="200" alt="Logo" src="https://user-images.githubusercontent.com/8766259/231213427-63ea2752-13d5-4993-aee2-90671b57fc6e.png"></td>
  </tr>
  <tr>
    <td>
      <a href="https://pypi.org/project/dxsp/"><img src="https://img.shields.io/pypi/v/dxsp?style=for-the-badge&logo=PyPI&logoColor=white"></a><br>
      <a href="https://pypi.org/project/dxsp/"><img src="https://img.shields.io/pypi/dm/dxsp?style=for-the-badge&logo=PyPI&logoColor=white&label=pypi&labelColor=grey"></a><br>
      <a href="https://github.com/mraniki/dxsp/"><img src="https://img.shields.io/github/actions/workflow/status/mraniki/dxsp/%F0%9F%91%B7Flow.yml?style=for-the-badge&logo=GitHub&logoColor=white"></a><br>
   <a href="https://talky.readthedocs.io/projects/findmyorder/index.html"><img src="https://readthedocs.org/projects/dxsp/badge/?version=latest&style=for-the-badge"></a><br>
   <a href="https://codebeat.co/projects/github-com-mraniki-dxsp-main"><img src="https://codebeat.co/badges/b1376839-73bc-4b41-bfc1-2fb099f1fc2a"/></a><br>
   <a href="https://codecov.io/gh/mraniki/dxsp"><img src="https://codecov.io/gh/mraniki/dxsp/branch/main/graph/badge.svg?token=39ED0ZA6IH"/> </a><br>
    </td>
    <td align="left"> 
Swap made easy<br>
Trade on any blockchains with uniswap based router or 0x protocol.
    </td>
     
  </tr>
</table>

<h5>How to use it</h5>
<pre>
<code>
   from dxsp import DexSwap
    dex = DexSwap()
    #BUY 10 USDT to SWAP with BITCOIN
    demo_tx = await dex.get_swap('USDT','wBTC',10)
    print("demo_tx ", demo_tx)
</code>
</pre>

<h5>Example</h5>

https://github.com/mraniki/dxsp/blob/f76fd035eddadc4de2a8509a7c26250c187b0658/examples/example.py#L1-L68

