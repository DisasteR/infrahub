/// <reference types="cypress" />

import { gql } from "@apollo/client";
import { MockedProvider } from "@apollo/client/testing";
import { Route, Routes } from "react-router-dom";
import { ObjectDetailsPage } from "../../../src/pages/objects/object-details";
import { schemaState } from "../../../src/state/atoms/schema.atom";
import {
  deviceDetailsMocksASNName,
  deviceDetailsMocksData,
  deviceDetailsMocksId,
  deviceDetailsMocksOwnerName,
  deviceDetailsMocksQuery,
  deviceDetailsMocksSchema,
  deviceDetailsMocksTagName,
  getPermissionsData,
  getPermissionsQuery,
} from "../../mocks/data/devices";
import { TestProvider } from "../../mocks/jotai/atom";

// URL for the current view
const graphqlQueryItemsUrl = `/objects/InfraDevice/${deviceDetailsMocksId}`;

// Path that will match the route to display the component
const graphqlQueryItemsPath = "/objects/:objectKind/:objectid";

// Mock the apollo query and data
const mocks: any[] = [
  {
    request: {
      query: gql`
        ${deviceDetailsMocksQuery}
      `,
      variables: { offset: 0, limit: 10 },
    },
    result: {
      data: deviceDetailsMocksData,
    },
  },
  // Permissions
  {
    request: {
      query: gql`
        ${getPermissionsQuery}
      `,
      variables: { offset: 0, limit: 10 },
    },
    result: {
      data: getPermissionsData,
    },
  },
];

// Provide the initial value for jotai
const ObjectDetailsProvider = () => {
  return (
    <TestProvider initialValues={[[schemaState, deviceDetailsMocksSchema]]}>
      <ObjectDetailsPage />
    </TestProvider>
  );
};

describe("List screen", () => {
  it("should fetch object details and render a list of details", () => {
    cy.viewport(1920, 1080);

    // Mount the view with the default route and the mocked data
    cy.mount(
      <MockedProvider mocks={mocks} addTypename={false}>
        <Routes>
          <Route element={<ObjectDetailsProvider />} path={graphqlQueryItemsPath} />
        </Routes>
      </MockedProvider>,
      {
        // Add iniital route for the app router, to display the current items view
        routerProps: {
          initialEntries: [graphqlQueryItemsUrl],
        },
      }
    );

    // The device ASN should be correctly named
    cy.contains("Asn").siblings().first().should("have.text", deviceDetailsMocksASNName);

    cy.contains("Asn")
      .siblings()
      .first()
      .within(() => {
        cy.get("[data-cy='metadata-button']").click();
      });

    cy.get("[data-cy='metadata-tooltip']").should("contain.text", deviceDetailsMocksOwnerName);

    cy.contains("Tags")
      .parent()
      .within(() => {
        cy.contains(deviceDetailsMocksTagName).should("be.visible");
      });
  });
});
