class Solution:
    def maximumUniqueSubarray(self, nums: List[int]) -> int:
        d={}
        ms=0
        s,j=0,0
        for i in range(len(nums)):
            s+=nums[i]
            d[nums[i]]=1+d.get(nums[i],0)
            while(d[nums[i]]>1):
                d[nums[j]]-=1
                s-=nums[j]
                j+=1
            ms=max(s,ms)
        return ms