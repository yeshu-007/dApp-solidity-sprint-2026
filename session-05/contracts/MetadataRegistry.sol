
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MetadataRegistry {
    address public owner;
    string public metadataURI;

    event MetadataUpdated(
        string metadataURI,
        address indexed updatedBy
    );

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorised");
        _;
    }

    function setMetadataURI(
        string memory newMetadataURI
    ) external onlyOwner {
        require(bytes(newMetadataURI).length > 0, "Empty URI");

        metadataURI = newMetadataURI;

        emit MetadataUpdated(newMetadataURI, msg.sender);
    }
}
