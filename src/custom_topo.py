from mininet.topo import Topo

N = 4


class MyTopo(Topo):
    def __init__(self, *args, **params):
        super().__init__(*args, **params)
        switch = self.addSwitch('s1')
        for h in range(N):
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch)


topos = {'mytopo': (lambda: MyTopo())}
