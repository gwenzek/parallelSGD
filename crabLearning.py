def loadData(dataFile):
    M = dict()
    nline = 0
    for line in open(dataFile, 'r'):
        l = line.split()
        (i, j, note) = (int(l[0]) - 1, int(l[1]) - 1, int(l[2]))
        if i in M:
            M[i][j] = note
        else:
            M[i] = {j: note}
        nline += 1

    print "loaded %d recommendations." % nline
    return(M)


def getRecommender(dataFile):
    from scikits.crab.models.classes import MatrixPreferenceDataModel
    model = MatrixPreferenceDataModel(loadData(dataFile))
    print model[0]
    from scikits.crab.metrics import pearson_correlation
    from scikits.crab.similarities import UserSimilarity
    similarity = UserSimilarity(model, pearson_correlation)
    from scikits.crab.recommenders.knn import UserBasedRecommender
    recommender = UserBasedRecommender(model, similarity, with_preference=True)
    a = 5
    print "For user %d we recommend movie %d" % (a, recommender.recommend(5))
    return recommender
