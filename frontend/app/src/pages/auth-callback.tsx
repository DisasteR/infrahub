import { Navigate, useParams, useSearchParams } from "react-router-dom";
import { useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useAtomValue } from "jotai";
import { configState } from "@/state/atoms/config.atom";
import { fetchUrl } from "@/utils/fetch";
import { INFRAHUB_API_SERVER_URL } from "@/config/config";

function AuthCallback() {
  const { protocol, provider } = useParams();
  const config = useAtomValue(configState);
  const [searchParams] = useSearchParams();
  const { isAuthenticated, setToken } = useAuth();
  const code = searchParams.get("code");
  const state = searchParams.get("state");
  const error = searchParams.get("error");

  useEffect(() => {
    if (!config || !config.sso.enabled) return;

    const currentAuthProvider = config.sso.providers.find(
      (p) => p.protocol === protocol && p.name === provider
    );
    if (!currentAuthProvider) return;

    const { token_path } = currentAuthProvider;
    fetchUrl(`${INFRAHUB_API_SERVER_URL}${token_path}?code=${code}&state=${state}`).then(
      (result) => {
        setToken(result);
      }
    );
  }, [config, protocol, provider]);

  if (!config || !config.sso.enabled) {
    return <Navigate to="/signin" replace />;
  }

  if (error) {
    return <Navigate to="/signin" replace />;
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return null;
}

export const Component = AuthCallback;