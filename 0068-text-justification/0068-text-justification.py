class Solution:
    def fullJustify(self, words: List[str], maxWidth: int) -> List[str]:
        l=[]
        st=words[0]
        words.pop(0)
        for i in words:
            if(len(st)+1+len(i)<=maxWidth):
                st+=" "+i
            else:
                l.append(st)
                st=i
        l.append(st)
        l1=[]
        for idx,i in enumerate(l):
            s1=""
            c=i.count(" ")
            if(len(i)<maxWidth):
                a=maxWidth-len(i)
                if(c>0 and idx!=len(l)-1):
                    k=a%c
                    o=a//c
                    b=0
                    for j in i:
                        s1+=j
                        if(j==" "):
                            s1+=" "*o
                            if(b<k):
                                s1+=" "
                                b+=1
                    l1.append(s1)
                else:
                    s1=i+" "*a
                    l1.append(s1)
            if(len(i)==maxWidth):
                l1.append(i)
        return l1
                