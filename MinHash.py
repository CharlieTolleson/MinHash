import numpy as np
import hashlib
import random


class MinHash():
    
    def __init__(self, n_bits, n_hashes, jaccard_threshold = 0.8, shingle_size = 5, 
                 hash_func = hashlib.sha3_256, rand_seed = None):
        
        self.n_bits = n_bits
        self.n_hashes = n_hashes
        self.jaccard_threshold = jaccard_threshold
        self.shingle_size = shingle_size
        self.hash_func = hash_func
        self.index = {}
        
        random.seed(rand_seed)
        self.rand_bit_strings = np.array([random.getrandbits(n_bits) for i in range(n_hashes)])
        
        
    def generate_shingles(self, text):
        split_text = text.split()
        
        tokens = []
        for i in range(len(split_text) - self.shingle_size):
            tokens.append(' '.join(split_text[i:i+self.shingle_size]).encode('utf-8'))
            
        return tokens
    
    
    def generate_fingerprint(self, tokens):
        
        hashes = np.array([int(self.hash_func(token).hexdigest(), 16) % 2**self.n_bits for token in tokens])
        
        hashes_arr = np.repeat(hashes.reshape(-1, 1), self.n_hashes, axis = 1)
        
        all_hashes = np.bitwise_xor(hashes_arr, self.rand_bit_strings)
        
        fingerprint = np.min(all_hashes, axis = 0)
        
        hash_id_fingerprint = []
        for i in range(self.n_hashes):
            hash_id_fingerprint.append(str(i) + ':' + str(fingerprint[i]))
        
        return hash_id_fingerprint
    
    
    def jaccard_similarity(self, list1, list2):
        intersection = len(list(set(list1).intersection(list2)))
        
        union = (len(list1) + len(list2)) - intersection
        
        return float(intersection) / union
    
    
    def compare(self, shingles, candidate_documents):
        
        for cand_text in candidate_documents:
            cand_shingles = self.generate_shingles(cand_text)
            
            if self.jaccard_similarity(shingles, cand_shingles) >= self.jaccard_threshold:
                return True
            
        return False
    
    
    def process_documents(self, documents):
        duplicates = []
        
        for doc_id in documents:
            shingles = self.generate_shingles(documents[doc_id])
            fingerprint = self.generate_fingerprint(shingles)
            
            duplicate = False
            for finger in fingerprint:
                                                       
                if self.index.get(finger) is not None:
                    candidate_documents = [documents[cand_id] for cand_id in self.index[finger]]
                    duplicate = self.compare(shingles, candidate_documents)
                    
                    if duplicate:
                        duplicates.append(doc_id)
                        break
                        
            if not duplicate:
                for finger in fingerprint:
                    if self.index.get(finger) is None:
                        self.index[finger] = [doc_id]
                    else:
                        self.index[finger].append(doc_id)
                
        for duplicate_id in duplicates:
            del documents[duplicate_id]
            
        print('duplicates found: ' + str(len(duplicates)))
            
        return documents




if __name__ == "__main__":

    text = '''Amy Klobuchar: The Minnesota senator benefited the most from the smaller number of candidates on stage. She got to talk a LOT more than in past debates and used that time very, very well. She started strong -- outshining her competitors with her answer on how to convince the public that the impeachment was the right move. Time and time again in answer after answer, Klobuchar drove home her basic message: I'm from the Midwest. I'm a woman. I get things done. And, she effectively took it to South Bend, Indiana, Mayor Pete Buttigieg over his dismissiveness of service in the Senate. An excellent debate performance when Klobuchar really needed one.
    Joe Biden: I'm not sure whether it was the smaller number of candidates on stage or a renewed confidence in his status as the front-runner in the race. But, what I am sure of is that -- from beginning to end -- this was the former vice president's best debate, by a lot. His answer on the need to build consensus and work with Republicans -- noting that he more than anyone else on the stage had reason not to like Republicans who have spent attacking he and his son, Hunter, for months -- was his best answer in any debate. Biden's response to questions about his age -- he said age brought him much-needed experience and wisdom -- was self assured and solid. Biden was simply more confident and competent Thursday night -- just look at how he directly took on Sen. Bernie Sanders on "Medicare for All" -- than he has been in prior debates.
    Andrew Yang: There were six politicians on stage in Los Angeles on Thursday night. And one Andrew Yang. Yang's answers on any question he was asked were miles away from how his rivals answered them. Hell, he talked about thorium! His answer on being the lone non-white candidate on the stage -- he called it "an honor and a disappointment" -- was eloquent. He spoke from personal experience about how best to address the challenges and opportunities of raising a special needs child. (One of Yang's sons has autism.) And, when talking about whether politics needed more women, Yang said this: "The fact is ... if you get too many men alone and leave us alone for a while, we kind of become morons." Amen, Andrew.'''

    documents = {'A': text,
                 'B': text[:-800],
                 'C': text[:1600]}
    
    mh = MinHash(n_bits = 31, n_hashes = 3, jaccard_threshold = 0.8, shingle_size = 5)
    
    docs = mh.process_documents(documents)

    print(mh.index)

