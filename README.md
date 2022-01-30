
# Natural Language Processing for RFP Similarity

## Motivation and background

This project uses a natural language processing (NLP) algorithm to allow the matching of potential requests for proposals (RFP's) to existing proposals that have been already prepared and delivered.

The motivation for this solution is multifaceted:

1) Proposals contain substantial boilerplate text. If a similar proposal has already been prepared this can significantly reduce the time required to produce this text.

2) Finding the correct team is imperative to winning a proposal. Identifying similar completed proposals allows for a proposal manager to identify relevant personnel quickly.

3) Similar projects are undertaken across the globe, and more often than not innovative ideas are not shared quickly or widely enough. By identifying similar proposals innovative solutions from far reaches of the globe can be assessed for their feasibility and perhaps implemented as a proposed solution to the RFP.


This project was undertaken by myself as a primarily learning based project. Although I think the solution has real world applications, the end result is not currently impressive enough to be used as an enterprise solution. I do believe that implementation of a more advanced algorithm may yield more promising results.

The project focused on the deployment of the algorithm into a serverless architecture and building a front end application that end users can interact with. In this sense, the python and machine learning aspect has taken a back seat.


## Architecture
***

![Rough Architecture flowchart](https://raw.githubusercontent.com/jmoro0408/RFP_NLP/main/Azure/HelperFuncs/Architecture.png?token=GHSAT0AAAAAABP4RZBHSQZDX6WSZKIGVXYQYPXC6XQ)

Initially, all proposals which are to be compared against must have their text extracted and uploaded to Azure blob storage. I used a  python package ([tika](https://pypi.org/project/tika/)) to do this locally and upload manually, however the Microsoft Computervision API could be accessed to allow uploading and extracting of new proposals in future.

The end user interacts with a basic Powerapps App that allows the uploading of a new RFP (referred to as the 'base document') into Azure blob storage. From here an Azure Function is triggered to begin analyzing the new base document.

The function accesses the blob storage container with the base document, calls the Microsoft Computervision API to extract the text from the document and write it to a .txt file which is saved in a new blob container for processed RFPs.

This processed RFP txt file is then compared to all proposals uploaded in the first step via an algorithm known as term frequency - inverse document frequency (tf-idf). This approximates how similar a block of text is to another.

The most similar documents have their titles saved along with relative scores into a results json file which is saved in a json results folder.

A power automate flow then reads this results json file and delivers the most similar documents and scores back to the end user.





