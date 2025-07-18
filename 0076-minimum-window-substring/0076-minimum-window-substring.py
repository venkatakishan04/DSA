class Solution:
    def minWindow(self, s: str, t: str) -> str:
        # venkatakishan04
        if(len(t)>len(s)):
            return ""
        c=Counter(t)
        l=0
        j=0
        si=-1
        ml=10**5
        for i in range(len(s)):
            c[s[i]]=-1+c.get(s[i],0)
            if(c[s[i]]>-1):
                l+=1
            while l==len(t) and j<=i:
                if i-j+1<ml:
                    ml=i-j+1
                    si=j
                c[s[j]]+=1
                if(c[s[j]]>0):
                    l-=1
                j+=1
        if(si==-1):
            return ""
        return s[si:si+ml]